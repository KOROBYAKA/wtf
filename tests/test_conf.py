import pytest
from copy import deepcopy
from wtf.conf import config_validation, build_iperf_cmd
from wtf.errors import InvalidFieldError, MissingFieldError, ConfigConflictError

def test_valid_config_passes(valid_config):
    config_validation(valid_config)
    assert True

def test_full_valid_defaults(valid_config):
    defaults = valid_config["defaults"]
    cmd = build_iperf_cmd(defaults)
    assert cmd == "-t 15 -b 0 -l 0 --bidir --dont-fragment --reverse"

def test_config_overflow_ip(valid_config):
    config = deepcopy(valid_config)
    config["ap_conf"]["ap_ctrl_ip"] = "1.1.1.256"
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(config)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message
    assert "ap_ctrl_ip" in error_message
    assert "1.1.1.256" in error_message

def test_config_negative_ip(valid_config):
    config = deepcopy(valid_config)
    config["ap_conf"]["ap_ctrl_ip"] = "192.168.1.-1"
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(config)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message
    assert "ap_ctrl_ip" in error_message
    assert "192.168.1.-1" in error_message

def test_config_invalid_ip(valid_config):
    config = deepcopy(valid_config)
    config["ap_conf"]["ap_ctrl_ip"] = "192.168.1.1.not.even.ip"
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(config)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message
    assert "ap_ctrl_ip" in error_message
    assert "192.168.1.1.not.even.ip" in error_message

def test_config_invalid_same_ip(valid_config):
    config = deepcopy(valid_config)
    config["ap_conf"]["ap_ctrl_ip"] = config["ap_conf"]["ap_wifi_ip"]
    with pytest.raises(ConfigConflictError) as exc_info:
        config_validation(config)

    error_message = str(exc_info.value)
    assert "ap_wifi_ip" in error_message
    assert "ap_ctrl_ip" in error_message
    assert "must be different" in error_message

def test_config_invalid_exec_mode(valid_config):
    config = deepcopy(valid_config)
    config["execution_mode"] = 3
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(config)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message
    assert "execution_mode" in error_message
    assert "3" in error_message

def test_config_no_exec_mode(valid_config):
    config = deepcopy(valid_config)
    del config["execution_mode"]

    with pytest.raises(MissingFieldError) as exc_info:
        config_validation(config)

    error_message = str(exc_info.value)
    assert "Missing required configuration field" in error_message
    assert "execution_mode" in error_message

def test_config_empty_config():
    with pytest.raises(MissingFieldError) as exc_info:
        config_validation({})

    error_message = str(exc_info.value)
    assert "Missing required configuration field" in error_message

def test_config_empty_fields(empty_fields_config):
    config = deepcopy(empty_fields_config)

    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(config)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message

def test_shortest_defaults():
    minimal_defaults = {
        "timeout": 15}

    short_defaults = {
    "timeout": 15,
    "bidir": 0,
    "reverse": 0,
    "fragmentation": 1,
    }

    min_cmd1 = build_iperf_cmd(minimal_defaults)
    min_cmd2 = build_iperf_cmd(short_defaults)

    assert min_cmd1 == min_cmd2