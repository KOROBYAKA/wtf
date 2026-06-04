
import pytest

@pytest.fixture
def valid_config():
    return {
        "execution_mode": 1,
        "client_conf": {
            "cl_wifi_ip": "192.168.1.2",
            "cl_ctrl_ip": "192.168.2.2",
        },
        "ap_conf": {
            "ap_wifi_ip": "192.168.1.1",
            "ap_ctrl_ip": "192.168.2.1",
            "uci_ap_iface": "radio0",
            "ap_wifi_iface": "phy0-ap0",
            "ap_phy": "phy0",
        },
        "defaults": {
            "timeout": 15,
            "bandwidth": 0,
            "packet_length": 0,
            "bidir": 1,
            "reverse": 1,
            "fragmentation": 0,
        },
    }

@pytest.fixture
def empty_fields_config():
    return {
        "execution_mode": None,
        "client_conf": {
            "cl_wifi_ip": None,
            "cl_ctrl_ip": None,
        },
        "ap_conf": {
            "ap_wifi_ip": None,
            "ap_ctrl_ip": None,
            "uci_ap_iface": None,
            "ap_wifi_iface": None,
            "ap_phy": None,
        },
        "defaults": {
            "timeout": None,
            "bandwidth": None,
            "packet_length": None,
            "bidir": None,
            "reverse": None,
            "fragmentation": None,
        },
    }

class FakeClient():
    def __init__(self,ip):
        self.state = 0 #close
        self.ip = ip
    def open(self):
        if self.state == 0:
            self.state = 1

    def close(self):
        if self.state == 1:
            self.state = 0

    def get_state(self):
        return self.state

    def get_ip(self):
        return self.ip

@pytest.fixture
def get_fake_client():
    def fake_get_client(ip):
        client = FakeClient(ip)
        client.open()
        return client

    return fake_get_client
