import tomllib
import ipaddress
import pathlib
from wtf.tooling import REQUIRED_FIELDS, IP_FIELDS, debug_printer
from wtf.errors import MissingFieldError, InvalidFieldError, ConfigConflictError, MissingSectionError

#Reads .toml config on specified path
#Retuns dict
@debug_printer
def load_config(path):
    with open(pathlib.Path(path), mode="rb") as fp:
        config = tomllib.load(fp)
        return config


#Returns a command to run iperf
@debug_printer
def build_iperf_cmd(args, src_ip, dst_ip):
    command = [
        "iperf3",
        "-c", f"{dst_ip}",
        "-B", f"{src_ip}",
        "-t", f"{args['timeout']}",
        "-i", f"{args['timeout']}",
        "-J"]
    if "bandwidth" in args:
        command.append(f"-b {args['bandwidth']}")
    if "packet_length" in args:
        command.append(f"-l {args['packet_length']}")
    if "fragmentation" in args and args["fragmentation"] == 0:
        command.append("--dont-fragment")

    return command

#Returns a command to run ping
def build_ping_cmd(source_ip, target_ip, freq, duration):
    ping_interval = 1/freq
    ping_amount = int(freq * (duration*0.8))
    return [
        "/bin/ping",
        f"{target_ip}",
        "-I", f"{source_ip}",
        "-c", f"{ping_amount}",
        "-i", f"{ping_interval}"
    ]


@debug_printer
def config_validation(config):

    if "execution_mode" not in config.keys():
        raise MissingFieldError("ROOT","execution_mode")

    for section, fields in REQUIRED_FIELDS.items():
        if section not in config:
            raise MissingSectionError(section)
        for field in fields:
            if field not in config[section]:
                raise MissingFieldError(section, field)

    if config["execution_mode"] not in (0, 1):
        raise InvalidFieldError("execution_mode", config["execution_mode"])

    used_ips = {}

    for section, fields in IP_FIELDS.items():
        for field in fields:
            value = config[section][field]
            try:
                ipaddress.ip_address(value)
                if value in used_ips.keys():
                    prev_field, prev_section = used_ips[value]
                    raise ConfigConflictError(
                        f"The value {value} for field {field} in section {section} is already used by the field {prev_field} in section {prev_section}.Values for all IP addresses must be different")
                used_ips[value] = (section, field)
            except ValueError:
                raise InvalidFieldError(field, value)

    if config["ap_conf"]["ap_wifi_ip"] == config["client_conf"]["cl_wifi_ip"]:
        raise ConfigConflictError("ap_wifi_ip and cl_wifi_ip must be different")

    if config["ap_conf"]["ap_ctrl_ip"] == config["client_conf"]["cl_ctrl_ip"]:
        raise ConfigConflictError("ap_ctrl_ip and cl_ctrl_ip must be different")