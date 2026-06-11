import pytest
from assertpy import assert_that
from wtf.conf import config_validation, build_iperf_cmd, build_ping_cmd, load_config
from wtf.errors import InvalidFieldError, MissingFieldError, ConfigConflictError

def test_valid_config_passes(valid_config_exec0):
    config_validation(valid_config_exec0)
    assert True

def test_full_valid_defaults(valid_config_exec0):
    cmd = build_iperf_cmd(valid_config_exec0["iperf_args"], "192.168.1.1", "192.168.1.2")
    premade = ["iperf3","-t","15", "-b","0", "-l", "0","-J", "--dont-fragment", "-B" ,"192.168.1.1", "-c", "192.168.1.2",
               "-i","15"]

    assert_that(sorted(cmd)).is_equal_to(sorted(premade))

def test_config_overflow_ip(invalid_config_overflow_ip):
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(invalid_config_overflow_ip)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message
    assert "cl_wifi_ip" in error_message
    assert "192.168.1.256" in error_message

def test_config_negative_ip(invalid_config_negative_ip):
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(invalid_config_negative_ip)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message
    assert "cl_wifi_ip" in error_message
    assert "192.168.1.-1" in error_message

def test_config_invalid_ip(invalid_config_invalid_ip):
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(invalid_config_invalid_ip)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message
    assert "cl_wifi_ip" in error_message
    assert "192.168.1.IO" in error_message

def test_config_invalid_same_ip(invalid_config_duplicate_ip):
    with pytest.raises(ConfigConflictError) as exc_info:
        config_validation(invalid_config_duplicate_ip)

    error_message = str(exc_info.value)
    assert "cl_ctrl_ip" in error_message
    assert "ap_wifi_ip" in error_message
    assert "must be different" in error_message

def test_config_invalid_exec_mode(invalid_config_invalid_exec_mode):
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(invalid_config_invalid_exec_mode)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message
    assert "execution_mode" in error_message
    assert "514" in error_message

def test_config_no_exec_mode(invalid_config_no_exec_mode):
    with pytest.raises(MissingFieldError) as exc_info:
        config_validation(invalid_config_no_exec_mode)

    error_message = str(exc_info.value)
    assert "Missing required configuration field" in error_message
    assert "execution_mode" in error_message

def test_config_empty_config():
    with pytest.raises(MissingFieldError) as exc_info:
        config_validation({})

    error_message = str(exc_info.value)
    assert "Missing required configuration field" in error_message

def test_config_empty_fields(invalid_config_empty):
    with pytest.raises(InvalidFieldError) as exc_info:
        config_validation(invalid_config_empty)

    error_message = str(exc_info.value)
    assert "Invalid configuration field" in error_message

def test_iperf_cmd(valid_config_exec0):
    args = {
    "timeout": 15,
    "bidir": 0,
    "reverse": 0,
    "fragmentation": 0,
    "bandwidth": 0,
    "packet_length": 0,
    }
    conf_args = valid_config_exec0["iperf_args"]

    min_cmd1 = build_iperf_cmd(args, "192.168.1.1", "192.168.1.2")
    min_cmd2 = build_iperf_cmd(conf_args,"192.168.1.1", "192.168.1.2")

    assert min_cmd1 == min_cmd2