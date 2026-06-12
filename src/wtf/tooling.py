import subprocess
from functools import wraps
import ipaddress
from wtf.errors import InvalidIPAddressError

_debug_enabled = False

def set_debug(enabled: bool) -> None:
    global _debug_enabled
    _debug_enabled = enabled

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
    "directions":[
        "client_to_ap",
        "ap_to_client",
        "bidirectional",
    ],
    "transport":[
        "tcp",
        "udp",
    ],
    "iperf_args":[
        "timeout",
        "bandwidth",
        "packet_length",
        "fragmentation",
    ],
    "ping_args":[
        "frequency",
    ]
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

def connection_status(target_ip, bind_ip = 0):

    try:
        ipaddress.ip_address(target_ip)
    except ValueError:
        raise InvalidIPAddressError(f"{target_ip} is not a valid IP address that can be pinged")

    if bind_ip:
        cmd = [f"ping {target_ip} -c 1 -W 1 -I {bind_ip}"]
        try:
            ipaddress.ip_address(bind_ip)
        except ValueError:
            raise InvalidIPAddressError(f"{bind_ip} is not a valid IP address that can be pinged")
    else:
        cmd = [f"ping {target_ip} -c 1 -W 1"]
    print("#", " ".join(cmd))
    ping_res_ip = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if ping_res_ip.returncode == 0:
        print('CONNECTION STATUS: The node is reachable')
        return True
    else:
        print('The node is offline')
        return False

def get_directions(dirs: dict, execution_mode: int) -> list[dict]:
    directions = {}

    if dirs["client_to_ap"] == 1:
        if execution_mode == 1:
            iperf_flag = "--reverse"
        elif execution_mode == 0:
            iperf_flag = ""

        directions["client_to_ap"]= iperf_flag

    if dirs["ap_to_client"] == 1:
        if execution_mode == 1:
            iperf_flag = ""
        elif execution_mode == 0:
            iperf_flag = "--reverse"

        directions["ap_to_client"]= iperf_flag

    if dirs["bidirectional"] == 1:
        directions["bidirectional"] = "--bidir"

    return directions


def debug_printer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if _debug_enabled:
            print("#DEBUG")
            print(f"Executing: {func.__name__}")
        return func(*args, **kwargs)

    return wrapper



