from wtf.ap import Ap
import wtf.ap as ap_module
from copy import deepcopy

def test_ap_execution_mode_0(valid_config_exec0):
    ap = Ap.build_ap(valid_config_exec0)

    assert ap.execution_mode == 0
    assert ap.ap_ctrl_ip == ap.control_target_ip
    assert ap.remote_wifi_ip == ap.ap_wifi_ip
    assert ap.local_wifi_ip == ap.cl_wifi_ip


def test_ap_execution_mode_1(valid_config_exec1):
    ap = Ap.build_ap(valid_config_exec1)

    assert ap.execution_mode == 1
    assert ap.cl_ctrl_ip == ap.control_target_ip
    assert ap.remote_wifi_ip == ap.cl_wifi_ip
    assert ap.local_wifi_ip == ap.ap_wifi_ip

def test_ap_close_client_if_no_client_created(valid_config_exec0):
    ap = Ap.build_ap(valid_config_exec0)
    ap.close_ssh()

    assert ap.client is None

def test_set_ssh(valid_config_exec0, monkeypatch, get_fake_client):
    monkeypatch.setattr(ap_module, "get_client", get_fake_client)

    ap = Ap.build_ap(valid_config_exec0)
    ap.set_ssh()
    assert ap.client.get_ip() == ap.control_target_ip
    assert ap.client.get_state() == 1


def test_close_ssh(valid_config_exec0, monkeypatch, get_fake_client):
    monkeypatch.setattr(ap_module, "get_client", get_fake_client)

    ap = Ap.build_ap(valid_config_exec0)
    ap.set_ssh()
    ap.close_ssh()

    assert ap.client.get_ip() == ap.control_target_ip
    assert ap.client.get_state() == 0
