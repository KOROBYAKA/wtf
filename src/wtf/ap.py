import subprocess
from wtf.tooling import run_cmd, debug_printer
from wtf.ssh_connection import get_client, remote_execution
from wtf.errors import APDisabledError

class Ap():
    def __init__(self,
        uci_ap_iface: str,
        ap_wifi_iface: str,
        ap_phy: str,
        ap_wifi_ip: str,
        ap_ctrl_ip: str,
        cl_wifi_ip: str,
        cl_ctrl_ip: str,
        execution_mode: int,):
        # OpenWrt / Wi-Fi device identifiers
        self.uci_ap_iface = uci_ap_iface
        self.ap_wifi_iface = ap_wifi_iface
        self.ap_phy = ap_phy

        # Test/data plane IPs
        self.ap_wifi_ip = ap_wifi_ip
        self.cl_wifi_ip = cl_wifi_ip

        # Management/control plane IPs
        self.ap_ctrl_ip = ap_ctrl_ip
        self.cl_ctrl_ip = cl_ctrl_ip

        # 1 = WTF runs on AP
        # 0 = WTF runs on client/controller machine
        self.execution_mode = execution_mode

        if execution_mode == 1:
            self.local_wifi_ip = self.ap_wifi_ip
            self.remote_wifi_ip = self.cl_wifi_ip
            self.control_target_ip = self.cl_ctrl_ip
        elif execution_mode == 0:
            self.local_wifi_ip = self.cl_wifi_ip
            self.remote_wifi_ip = self.ap_wifi_ip
            self.control_target_ip = self.ap_ctrl_ip
        else:
            raise ValueError("execution_mode must be 1 for AP mode or 0 for client mode")

        self.client = None
        self.iperf_cmd = None



    @debug_printer
    def set_ssh(self):
        # SSH Client connection
        self.client = get_client(self.control_target_ip)

    @debug_printer
    def get_wifi_capabilities(self):
        cmds = [f"iwinfo {self.ap_phy} htmodelist",
                f"iwinfo {self.ap_phy} freq"]
        wifi_channels_list = []
        if self.execution_mode == 1:
            ht_modes = subprocess.run(cmds[0], shell=True, capture_output=True, text=True).stdout
            wifi_channels = subprocess.run(cmds[1], shell=True, capture_output=True, text=True)
            for line in wifi_channels.stdout.split("\n"):
                try:
                    wifi_channels_list.append(line.strip(" *()\\|/").split(" ")[6].strip(")"))
                except Exception as e:
                    print(f"Error: {e}")
                    raise SystemExit(1)

        if self.execution_mode == 0:
                output = remote_execution(client = self.client, cmds = cmds)
                for line in output[1].split("\n"):
                    try:
                        wifi_channels_list.append(line.strip(" *()\\|/").split(" ")[6].strip(")"))
                    except Exception as e:
                        print(f"Error: {e}")
                        raise SystemExit(1)
                ht_modes = output[0]
        return wifi_channels_list, ht_modes.split()

    @debug_printer
    def set_wifi_capabilities_OpenWrt(self,channel:int, ht_mode:str):
        #Due to the target OS is an OpenWRT, UCI configuration interface
        #is used to set up desirable Wi-Fi Capabilities
        #If you want use it on another
        cmds = [f"uci set wireless.{self.uci_ap_iface}.channel='{channel}'",
                f"uci set wireless.{self.uci_ap_iface}.htmode='{ht_mode}'",
                "uci commit",
                "wifi reload"]
        if self.execution_mode == 1:
            for cmd in cmds:
                subprocess.run(cmd, shell=True, check=True, text=True)

        if self.execution_mode == 0:
            _ = remote_execution(client = self.client, cmds = cmds)

    @debug_printer
    def getter(self):
        args = ['tx_bytes', 'rx_bytes', 'tx_packets', 'rx_packets']
        cmd_base = f'cat /sys/class/net/{self.ap_wifi_iface}/statistics/'
        cmds = {}
        for arg in args:
            cmd = cmd_base + arg
            cmds[arg] = cmd
        result = {}
        if self.execution_mode == 1:
            for arg, cmd in cmds.items():
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                stdout = res.stdout
                result[arg] = stdout

        if self.execution_mode == 0:
            for arg, cmd in cmds.items():
                output = remote_execution(self.client, [cmd])
                result[arg] = output[0]

        return result

    @debug_printer
    def ap_status(self):
        if self.execution_mode == 1:
            cmd = f"uci show.wireless.{self.uci_ap_iface}.disabled"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if "uci: Entry not found" in result.stdout:
                raise APDisabledError(f"The Access Point {self.uci_ap_iface} is disabled (check UCI and config)")

    @debug_printer
    def ap_link_status(self):
        cmd = f"dmesg | tail -n 10"
        if self.execution_mode == 1:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout.find("link becomes ready"):
                return True
            return False

        if self.execution_mode == 0:
            output = remote_execution(self.client,[cmd])[0]
            if output.find("link becomes ready"):
                return True
            return False

    @debug_printer
    def run_test(self, timeout):
        net_data_before_test = self.getter()
        _ = remote_execution(client =self.client, cmds = ["iperf3 -s -D"])
        run_cmd(f"iperf3 -c {self.remote_wifi_ip} -B {self.local_wifi_ip} -b 0 -t {timeout}")
        net_data_after_test = self.getter()
        _ = remote_execution(client = self.client, cmds = ["killall iperf3"])

        #results calculation
        delta = {}
        for key in net_data_before_test.keys():
            delta[key] = int(net_data_after_test[key].strip()) - int(net_data_before_test[key].strip())

        return delta

    @debug_printer
    def generate_metadata(self) -> dict:
        return self.__dict__




