import re

def parse_iperf_result(raw: dict, execution_mode: int) -> dict:
    end = raw["end"]
    bidir = raw["start"]["test_start"]["bidir"] == 1

    # execution_mode 1 =  AP → TX then AP→Client
    # execution_mode 0 = wtf runs on client → TX then Client→AP
    if execution_mode == 1:
        tx_label = "ap_to_client_mbps"
        rx_label = "client_to_ap_mbps"
        host_label = "cpu_ap"
        remote_label = "cpu_client"
    else:
        tx_label = "client_to_ap_mbps"
        rx_label = "ap_to_client_mbps"
        host_label = "cpu_client"
        remote_label = "cpu_ap"

    metrics = {
        "bidir": bidir,
        "duration": raw["start"]["test_start"]["duration"],

        tx_label: round(end["sum_sent"]["bits_per_second"] / 1e6, 2),
        "tx_retransmits": end["sum_sent"]["retransmits"],

        f"{host_label}_total": round(end["cpu_utilization_percent"]["host_total"], 2),
        f"{host_label}_user": round(end["cpu_utilization_percent"]["host_user"], 2),
        f"{host_label}_system": round(end["cpu_utilization_percent"]["host_system"], 2),

        f"{remote_label}_total": round(end["cpu_utilization_percent"]["remote_total"], 2),
        f"{remote_label}_user": round(end["cpu_utilization_percent"]["remote_user"], 2),
        f"{remote_label}_system": round(end["cpu_utilization_percent"]["remote_system"], 2),
    }

    if bidir:
        metrics[rx_label] = round(
            end["sum_received_bidir_reverse"]["bits_per_second"] / 1e6, 2
        )

    return metrics

def parse_ping_result(raw: str) -> dict:
    if not raw.strip():
        return {"error": "no ping output"}

    # parsing string "X packets transmitted, Y received, Z% packet loss"
    loss_match = re.search(
        r"(\d+) packets transmitted, (\d+) received, (\d+)% packet loss",
        raw
    )

    # parsing string "rtt min/avg/max/mdev = X/X/X/X ms"
    rtt_match = re.search(
        r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms",
        raw
    )

    result = {}

    if loss_match:
        result["packets_sent"] = int(loss_match.group(1))
        result["packets_recv"] = int(loss_match.group(2))
        result["packet_loss_pct"] = int(loss_match.group(3))

    if rtt_match:
        result["rtt_min_ms"] = float(rtt_match.group(1))
        result["rtt_avg_ms"] = float(rtt_match.group(2))
        result["rtt_max_ms"] = float(rtt_match.group(3))
        result["rtt_mdev_ms"] = float(rtt_match.group(4))

    if not result:
        raise RuntimeError(f"Failed to parse ping output:\n{raw}")

    return result


def create_data_record(
        iperf_record: dict,
        ap_to_client_ping: dict,
        client_to_ap_ping: dict,
) -> dict:
    def prefix_keys(d: dict, prefix: str) -> dict:
        return {f"{prefix}_{k}": v for k, v in d.items()}

    record = {}
    record.update(iperf_record)
    record.update(prefix_keys(ap_to_client_ping, "ping_ap_to_client"))
    record.update(prefix_keys(client_to_ap_ping, "ping_client_to_ap"))

    return record