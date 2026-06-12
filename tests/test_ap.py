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


def test_run_test_udp_adds_udp_flag(valid_config_exec0, monkeypatch):
    captured = {}

    def fake_remote_execution(client, cmds):
        return [""], [0]

    class FakeProc:
        def __init__(self, stdout):
            self._stdout = stdout

        def communicate(self):
            return self._stdout, b""

        def poll(self):
            return 0

        def send_signal(self, sig):
            pass

    def fake_run_iperf(self, cmd):
        captured["cmd"] = cmd
        return FakeProc(b'{"start":{"test_start":{}},"end":{}}')

    def fake_ping_local(self):
        return FakeProc(b"LOCAL PING OUTPUT")

    def fake_ping_remote(self, result_store):
        def worker():
            result_store["stdout"] = "REMOTE PING OUTPUT"
            result_store["returncode"] = 0

        return ap_module.Thread(target=worker)

    monkeypatch.setattr(ap_module, "remote_execution", fake_remote_execution)
    monkeypatch.setattr(Ap, "run_iperf", fake_run_iperf)
    monkeypatch.setattr(Ap, "ping_local", fake_ping_local)
    monkeypatch.setattr(Ap, "ping_remote", fake_ping_remote)
    monkeypatch.setattr(ap_module, "parse_iperf_result", lambda raw, mode: {})
    monkeypatch.setattr(ap_module, "parse_ping_result", lambda raw: {})
    monkeypatch.setattr(ap_module, "create_data_record", lambda iperf, ap_ping, cl_ping: {})
    monkeypatch.setattr(ap_module.time, "sleep", lambda _: None)

    ap = Ap.build_ap(valid_config_exec0)
    ap.client = object()
    ap.iperf_cmd = ["iperf3", "-c", ap.remote_wifi_ip]

    ap.run_test(direction="--reverse", transport="udp")

    assert captured["cmd"] == [
        "iperf3",
        "-c",
        ap.remote_wifi_ip,
        "--reverse",
        "-u",
    ]

def test_run_test_udp_adds_udp_flag(valid_config_exec0, monkeypatch):
    captured = {}

    def fake_remote_execution(client, cmds):
        return [""], [0]

    class FakeProc:
        def __init__(self, stdout):
            self._stdout = stdout

        def communicate(self):
            return self._stdout, b""

        def poll(self):
            return 0

        def send_signal(self, sig):
            pass

    def fake_run_iperf(self, cmd):
        captured["cmd"] = cmd
        return FakeProc(b'{"start":{"test_start":{}},"end":{}}')

    def fake_ping_local(self):
        return FakeProc(b"LOCAL PING OUTPUT")

    def fake_ping_remote(self, result_store):
        def worker():
            result_store["stdout"] = "REMOTE PING OUTPUT"
            result_store["returncode"] = 0

        return ap_module.Thread(target=worker)

    monkeypatch.setattr(ap_module, "remote_execution", fake_remote_execution)
    monkeypatch.setattr(Ap, "run_iperf", fake_run_iperf)
    monkeypatch.setattr(Ap, "ping_local", fake_ping_local)
    monkeypatch.setattr(Ap, "ping_remote", fake_ping_remote)
    monkeypatch.setattr(ap_module, "parse_iperf_result", lambda raw, mode: {})
    monkeypatch.setattr(ap_module, "parse_ping_result", lambda raw: {})
    monkeypatch.setattr(ap_module, "create_data_record", lambda iperf, ap_ping, cl_ping: {})
    monkeypatch.setattr(ap_module.time, "sleep", lambda _: None)

    ap = Ap.build_ap(valid_config_exec0)
    ap.client = object()
    ap.iperf_cmd = ["iperf3", "-c", ap.remote_wifi_ip]

    ap.run_test(direction="--reverse", transport="udp")

    assert captured["cmd"] == [
        "iperf3",
        "-c",
        ap.remote_wifi_ip,
        "--reverse",
        "-u",
    ]

def test_run_test_tcp_orchestration(valid_config_exec0, monkeypatch):
    calls = {
        "remote_cmds": [],
        "run_iperf_cmd": None,
    }

    def fake_remote_execution(client, cmds):
        calls["remote_cmds"].extend(cmds)

        if cmds == ["iperf3 -s -D"]:
            return [""], [0]

        if cmds == ["killall iperf3"]:
            return [""], [0]

        return ["REMOTE PING OUTPUT"], [0]

    class FakeProc:
        def __init__(self, stdout):
            self._stdout = stdout

        def communicate(self):
            return self._stdout, b""

        def poll(self):
            return 0

        def send_signal(self, sig):
            pass

    def fake_run_iperf(self, cmd):
        calls["run_iperf_cmd"] = cmd
        return FakeProc(b'{"start":{"test_start":{}},"end":{}}')

    def fake_ping_local(self):
        return FakeProc(b"LOCAL PING OUTPUT")

    def fake_ping_remote(self, result_store):
        def worker():
            result_store["stdout"] = "REMOTE PING OUTPUT"
            result_store["returncode"] = 0

        return ap_module.Thread(target=worker)

    def fake_parse_iperf_result(raw, execution_mode):
        return {
            "iperf_ok": True,
            "execution_mode": execution_mode,
        }

    def fake_parse_ping_result(raw):
        return {
            "ping_raw": raw,
        }

    def fake_create_data_record(iperf_record, ap_to_client_ping, client_to_ap_ping):
        return {
            "iperf": iperf_record,
            "ap_to_client_ping": ap_to_client_ping,
            "client_to_ap_ping": client_to_ap_ping,
        }

    monkeypatch.setattr(ap_module, "remote_execution", fake_remote_execution)
    monkeypatch.setattr(Ap, "run_iperf", fake_run_iperf)
    monkeypatch.setattr(Ap, "ping_local", fake_ping_local)
    monkeypatch.setattr(Ap, "ping_remote", fake_ping_remote)
    monkeypatch.setattr(ap_module, "parse_iperf_result", fake_parse_iperf_result)
    monkeypatch.setattr(ap_module, "parse_ping_result", fake_parse_ping_result)
    monkeypatch.setattr(ap_module, "create_data_record", fake_create_data_record)
    monkeypatch.setattr(ap_module.time, "sleep", lambda _: None)

    ap = Ap.build_ap(valid_config_exec0)
    ap.client = object()
    ap.iperf_cmd = ["iperf3", "-c", ap.remote_wifi_ip]

    result = ap.run_test(direction="--reverse", transport="tcp")

    assert "iperf3 -s -D" in calls["remote_cmds"]
    assert "killall iperf3" in calls["remote_cmds"]
    assert calls["run_iperf_cmd"] == [
        "iperf3",
        "-c",
        ap.remote_wifi_ip,
        "--reverse",
    ]

    assert result == {
        "iperf": {
            "iperf_ok": True,
            "execution_mode": ap.execution_mode,
        },
        "ap_to_client_ping": {
            "ping_raw": "REMOTE PING OUTPUT",
        },
        "client_to_ap_ping": {
            "ping_raw": "LOCAL PING OUTPUT",
        },
    }