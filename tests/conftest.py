import json
from pathlib import Path
import pytest
import pathlib
import tomllib

@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / ("fixtures")

@pytest.fixture
def valid_config_exec0(fixtures_dir):
    path = (fixtures_dir / "valid_config_exec0.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def valid_config_exec1(fixtures_dir):
    path = (fixtures_dir / "valid_config_exec1.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def invalid_config_invalid_ip(fixtures_dir):
    path = (fixtures_dir / "invalid_config_invalid_ip.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def invalid_config_negative_ip(fixtures_dir):
    path = (fixtures_dir / "invalid_config_negative_ip.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def invalid_config_overflow_ip(fixtures_dir):
    path = (fixtures_dir / "invalid_config_overflow_ip.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def invalid_config_duplicate_ip(fixtures_dir):
    path = (fixtures_dir / "invalid_config_duplicate_ip.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def invalid_config_no_exec_mode(fixtures_dir):
    path = (fixtures_dir / "invalid_config_no_exec_mode.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def invalid_config_invalid_exec_mode(fixtures_dir):
    path = (fixtures_dir / "invalid_config_invalid_exec_mode.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def invalid_config_empty(fixtures_dir):
    path = (fixtures_dir / "invalid_config_empty.toml")
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config

@pytest.fixture
def iperf_udp(fixtures_dir):
    with open(fixtures_dir / "iperf_udp.json") as f:
        return json.load(f)

@pytest.fixture
def iperf_udp_bidir(fixtures_dir):
    with open(fixtures_dir / "iperf_udp_bidir.json") as f:
        return json.load(f)

@pytest.fixture
def iperf_tcp_bidir(fixtures_dir):
    with open(fixtures_dir / "iperf_tcp_bidir.json") as f:
        return json.load(f)

@pytest.fixture
def iperf_tcp(fixtures_dir):
    with open(fixtures_dir / "iperf_tcp.json") as f:
        return json.load(f)

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
