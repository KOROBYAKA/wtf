import subprocess
import signal
import threading
from threading import Thread
from wtf.tooling import debug_printer, connection_status
from wtf.ssh_connection import get_client, remote_execution
from wtf.errors import InvalidIPAddressError
from wtf.conf import config_validation, build_iperf_cmd, build_ping_cmd
from wtf.telemetry_handling import parse_iperf_result, parse_ping_result, create_data_record



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

        #SSHClient object(paramiko)
        self.client = None
        #iperf3 command
        self.iperf_cmd = None
        #ping arguments dict
        self.ping_freq = 1
        self.test_duration = 1

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

    def make_iperf_cmd(self, args):
        self.iperf_cmd, self.test_duration = build_iperf_cmd(args, self.local_wifi_ip ,self.remote_wifi_ip)

    def get_iperf_cmd(self):
        return self.iperf_cmd

    def set_iperf_cmd(self, cmd):
        self.iperf_cmd = cmd

    def set_ping_freq(self, freq):
        self.ping_freq = freq

    @debug_printer
    def ip_access_check(self):
        if not connection_status(self.local_wifi_ip):
            raise InvalidIPAddressError(f"{self.local_wifi_ip} is offline or not reachable! Check connectivity or configuration.")

        if not connection_status(self.control_local_ip):
            raise InvalidIPAddressError(
                f"{self.control_local_ip} is offline or not reachable! Check connectivity or configuration.")

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
    def run_iperf(self, cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc

    @debug_printer
    def ping_local(self):
        cmd = build_ping_cmd(source_ip=self.local_wifi_ip, target_ip=self.remote_wifi_ip,
                             freq=self.ping_freq, duration=self.test_duration)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc

    @debug_printer
    def ping_remote(self, result_store):
        cmd = build_ping_cmd(
            source_ip=self.remote_wifi_ip,
            target_ip=self.local_wifi_ip,
            freq=self.ping_freq,
            duration=self.test_duration,
        )

        cmd_str = " ".join(cmd)

        def worker():
            outputs, codes = remote_execution(
                client=self.client,
                cmds=[cmd_str],
            )

            result_store["stdout"] = outputs[0]
            result_store["returncode"] = codes[0]

        return Thread(target=worker)

    @debug_printer
    def run_test(self, direction):
        _, _ = remote_execution(client=self.client, cmds=["iperf3 -s -D"])

        iperf_cmd = self.iperf_cmd + [direction]

        iperf_proc = None
        ping_proc = None
        remote_thread = None

        iperf_stdout = ""
        iperf_stderr = ""
        ping_stdout = ""
        ping_stderr = ""
        remote_result = {}

        try:
            iperf_proc = self.run_iperf(iperf_cmd)

            remote_thread = self.ping_remote(remote_result)
            remote_thread.start()

            ping_proc = self.ping_local()

            iperf_stdout, iperf_stderr = iperf_proc.communicate()
            ping_stdout, ping_stderr = ping_proc.communicate()

            remote_thread.join(timeout=self.test_duration)

        finally:
            if ping_proc is not None and ping_proc.poll() is None:
                ping_proc.send_signal(signal.SIGINT)
                ping_stdout, ping_stderr = ping_proc.communicate()

            if remote_thread is not None and remote_thread.is_alive():
                remote_thread.join(timeout=2)

            _, _ = remote_execution(client=self.client, cmds=["killall iperf3"])

        iperf_record = parse_iperf_result(iperf_stdout)

        local_ping_record = parse_ping_result(ping_stdout)
        remote_ping_record = parse_ping_result(remote_result.get("stdout", ""))

        if self.execution_mode == 1:
            ap_to_client_ping_result = local_ping_record
            client_to_ap_ping_result = remote_ping_record
        else:
            ap_to_client_ping_result = remote_ping_record
            client_to_ap_ping_result = local_ping_record

        data_record = create_data_record(
            iperf_record,
            ap_to_client_ping_result,
            client_to_ap_ping_result,
        )

        return data_record

    @debug_printer
    def generate_metadata(self) -> dict:
        return {
            "execution_mode": self.execution_mode,

            "uci_ap_iface": self.uci_ap_iface,
            "ap_wifi_iface": self.ap_wifi_iface,
            "ap_phy": self.ap_phy,

            "ap_wifi_ip": self.ap_wifi_ip,
            "ap_ctrl_ip": self.ap_ctrl_ip,
            "cl_wifi_ip": self.cl_wifi_ip,
            "cl_ctrl_ip": self.cl_ctrl_ip,

            "local_wifi_ip": self.local_wifi_ip,
            "remote_wifi_ip": self.remote_wifi_ip,
            "control_local_ip": self.control_local_ip,
            "control_target_ip": self.control_target_ip,

            "iperf_cmd": self.iperf_cmd,
        }


