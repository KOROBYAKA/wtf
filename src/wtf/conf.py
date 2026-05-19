import tomllib
from wtf.ap import Ap
import ipaddress
from wtf.tooling import REQUIRED_FIELDS, REQUIRED_ROOT_FIELDS, IP_FIELDS
from wtf.errors import MissingFieldError, InvalidFieldError, ConfigConflictError, MissingSectionError

def load_config():
    with open("conf.toml", mode="rb") as fp:
        config = tomllib.load(fp)
        return config

def check_defaults(defaults):
    command = [f'-t {defaults["timeout"]}']
    if "bandwidth" in defaults:
        command.append(f"-b {defaults['bandwidth']}")
    if "packet_length" in defaults:
        command.append(f"-l {defaults['packet_length']}")
    if "bidir" in defaults and defaults["bidir"] == 1:
        command.append("--bidir")
    if "fragmentation" in defaults and defaults["fragmentation"] == 0:
        command.append(f"--dont-fragment")
    if "reverse" in defaults and defaults["reverse"] == 1:
        command.append(f"--reverse")

    return ' '.join(command)

def config_validation(config):

    if config["execution_mode"] not in (0, 1):
        raise InvalidFieldError("execution_mode", config["execution_mode"])

    for section, fields in REQUIRED_FIELDS.items():
        if section not in config:
            raise MissingSectionError(section)
        for field in fields:
            if field not in config[section]:
                raise MissingFieldError(section, field)

    for section, fields in IP_FIELDS.items():
        for field in fields:
            value = config[section][field]
            try:
                ipaddress.ip_address(value)
            except ValueError:
                raise InvalidFieldError(field, value)

    if config["ap_conf"]["ap_wifi_ip"] == config["client_conf"]["cl_wifi_ip"]:
        raise ConfigConflictError("ap_wifi_ip and cl_wifi_ip must be different")

    if config["ap_conf"]["ap_ctrl_ip"] == config["client_conf"]["cl_ctrl_ip"]:
        raise ConfigConflictError("ap_ctrl_ip and cl_ctrl_ip must be different")

def build_ap(config):
    config_validation(config)

    ap = Ap(
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
