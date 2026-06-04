import subprocess
from wtf.tooling import run_cmd, debug_printer, connection_status
from wtf.ssh_connection import get_client, remote_execution
from wtf.errors import InvalidIPAddressError
from wtf.conf import config_validation

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
            self.control_local_ip = self.ap_ctrl_ip
        elif execution_mode == 0:
            self.local_wifi_ip = self.cl_wifi_ip
            self.remote_wifi_ip = self.ap_wifi_ip
            self.control_target_ip = self.ap_ctrl_ip
            self.control_local_ip = self.cl_ctrl_ip
        else:
            raise ValueError("execution_mode must be 1 for AP mode or 0 for client mode")

        self.client = None
        self.iperf_cmd = None

    @classmethod
    def build_ap(cls, config):
        config_validation(config)

        ap = cls(
            uci_ap_iface=config["ap_conf"]["uci_ap_iface"],
            ap_wifi_iface=config["ap_conf"]["ap_wifi_iface"],
            ap_phy=config["ap_conf"]["ap_phy"],

            ap_wifi_ip=config["ap_conf"]["ap_wifi_ip"],
            ap_ctrl_ip=config["ap_conf"]["ap_ctrl_ip"],

            cl_wifi_ip=config["client_conf"]["cl_wifi_ip"],
            cl_ctrl_ip=config["client_conf"]["cl_ctrl_ip"],

            execution_mode=config["execution_mode"],
        )

        return ap

    @debug_printer
    def ip_access_check(self):
        if not connection_status(self.local_wifi_ip, "127.0.0.1"):
            raise InvalidIPAddressError(f"{self.local_wifi_ip} is offline or not reachable! Check connectivity or configuration.")

        if not connection_status(self.control_target_ip):
            raise InvalidIPAddressError(
                f"{self.control_target_ip} is offline or not reachable! Check connectivity or configuration.")

        if not connection_status(self.remote_wifi_ip, self.local_wifi_ip):
            raise InvalidIPAddressError(
                f"{self.remote_wifi_ip} is offline or not reachable! Check connectivity or configuration.")

    @debug_printer
    def set_ssh(self):
        # SSH Client connection
        self.client = get_client(self.control_target_ip)

    @debug_printer
    def close_ssh(self):
        if self.client is not None:
            self.client.close()


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
                output, _ = remote_execution(client = self.client, cmds = cmds)
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
        #If you want use it on another OS
        #Customize it to the hostapd
        cmds = [f"uci set wireless.{self.uci_ap_iface}.channel='{channel}'",
                f"uci set wireless.{self.uci_ap_iface}.htmode='{ht_mode}'",
                "uci commit",
                "wifi reload"]
        if self.execution_mode == 1:
            for cmd in cmds:
                subprocess.run(cmd, shell=True, check=True, text=True)

        if self.execution_mode == 0:
            _, _ = remote_execution(client = self.client, cmds = cmds)

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
                output, _ = remote_execution(self.client, [cmd])
                result[arg] = output[0]

        return result

    @debug_printer
    def ap_preflight_check_OpenWrt(self):
        cmds = [
            f"uci -q show wireless.{self.uci_ap_iface}",
            f"iw {self.ap_wifi_iface} info",
            f"iwinfo {self.ap_phy} info"
        ]
        if self.execution_mode == 1:
            for cmd in cmds:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return False
            return True

        if self.execution_mode == 0:
            _, codes = remote_execution(self.client,cmds)
            if sum(codes) != 0:
                return False
            return True

        return False

    @debug_printer
    def link_status(self):
        if connection_status(self.control_target_ip, self.control_local_ip):
            return connection_status(self.remote_wifi_ip, self.local_wifi_ip)

        return False

    @debug_printer
    def run_test(self, timeout):
        net_data_before_test = self.getter()
        _, _ = remote_execution(client =self.client, cmds = ["iperf3 -s -D"])
        run_cmd(self.iperf_cmd)
        net_data_after_test = self.getter()
        _, _ = remote_execution(client = self.client, cmds = ["killall iperf3"])

        #results calculation
        delta = {}
        for key in net_data_before_test.keys():
            delta[key] = int(net_data_after_test[key].strip()) - int(net_data_before_test[key].strip())

        return delta

    @debug_printer
    def generate_metadata(self) -> dict:
        return self.__dict__




