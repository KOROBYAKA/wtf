from types import SimpleNamespace
import pytest
from wtf.errors import InvalidIPAddressError
from wtf.tooling import connection_status
import wtf.tooling as tooling


def test_connection_status_returns_true_when_ping_success(monkeypatch):
    def fake_run(cmd, shell, text, capture_output):
        assert cmd == ["ping 192.168.1.1 -c 1 -W 1"]
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(tooling.subprocess, "run", fake_run)

    assert connection_status("192.168.1.1") is True


def test_connection_status_returns_false_when_ip_overflow(monkeypatch):
    def fake_run(cmd, shell, text, capture_output):
        if cmd == ["ping 192.168.1.1 -c 1 -W 1"]:
            return SimpleNamespace(returncode=0)
        else:
            return SimpleNamespace(returncode=1)

    monkeypatch.setattr(tooling.subprocess, "run", fake_run)

    with pytest.raises(InvalidIPAddressError) as exc_info:
        connection_status("192.168.1.256")

    err_msg = str(exc_info.value)
    assert "not a valid IP address" in err_msg
    assert "192.168.1.256" in err_msg


def test_connection_status_returns_false_when_ip_negative(monkeypatch):
    def fake_run(cmd, shell, text, capture_output):
        if cmd == ["ping 192.168.1.1 -c 1 -W 1"]:
            return SimpleNamespace(returncode=0)
        else:
            return SimpleNamespace(returncode=1)

    monkeypatch.setattr(tooling.subprocess, "run", fake_run)

    with pytest.raises(InvalidIPAddressError) as exc_info:
        connection_status("192.168.1.-1")

    err_msg = str(exc_info.value)
    assert "not a valid IP address" in err_msg
    assert "192.168.1.-1" in err_msg

def test_connection_status_returns_false_when_invalid_ip(monkeypatch):
    def fake_run(cmd, shell, text, capture_output):
        if cmd == ["ping 192.168.1.1 -c 1 -W 1"]:
            return SimpleNamespace(returncode=0)
        else:
            return SimpleNamespace(returncode=1)

    monkeypatch.setattr(tooling.subprocess, "run", fake_run)

    with pytest.raises(InvalidIPAddressError) as exc_info:
        connection_status("192.168.1.256.no.ip")

    err_msg = str(exc_info.value)
    assert "not a valid IP address" in err_msg
    assert "192.168.1.256.no.ip" in err_msg