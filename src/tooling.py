import subprocess
import time

REQUIRED_ROOT_FIELDS = [
    "execution_mode",
]

REQUIRED_FIELDS = {
    "ap_conf": [
        "uci_ap_iface",
        "ap_wifi_iface",
        "ap_phy",
        "ap_wifi_ip",
        "ap_ctrl_ip",
    ],
    "client_conf": [
        "cl_wifi_ip",
        "cl_ctrl_ip",
    ],
}

IP_FIELDS = {
    "ap_conf": [
        "ap_wifi_ip",
        "ap_ctrl_ip",
    ],
    "client_conf": [
        "cl_wifi_ip",
        "cl_ctrl_ip",
    ],
}

def connection_status(target_ip):
    cmd = [f"ping {target_ip} -c 1 -W 1"]
    print("#", " ".join(cmd))
    ping_res_ip = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if ping_res_ip.returncode == 0:
        print('CONNECTION STATUS: The node is reachable')
        return True
    else:
        print('The node is offline')
        return False

def run_cmd(cmd:str):
    print(f"#{cmd}")
    subprocess.run(cmd, shell=True)
    time.sleep(0.1)









