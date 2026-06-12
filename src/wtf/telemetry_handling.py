import re

def parse_iperf_result(raw: dict, execution_mode: int) -> dict:
    end = raw["end"]
    test_start = raw["start"]["test_start"]
    bidir = test_start["bidir"] == 1
    reverse = test_start["reverse"] == 1

    sent_mbps = round(end["sum_received"]["bits_per_second"] / 1e6, 2)
    recv_mbps = round(end["sum_received_bidir_reverse"]["bits_per_second"] / 1e6, 2) if bidir else None

    if execution_mode == 1 and not reverse or execution_mode == 0 and reverse:
        ap_to_client = sent_mbps
        client_to_ap = recv_mbps
    else:
        ap_to_client = recv_mbps
        client_to_ap = sent_mbps

    cpu = end["cpu_utilization_percent"]

    if execution_mode == 1:
        host, remote = "ap", "client"
    else:
        host, remote = "client", "ap"

    return {
        "status": "ok",
        "bidir": bidir,
        "reverse": reverse,
        "duration": test_start["duration"],
        "throughput": {
            "ap_to_client": ap_to_client,
            "client_to_ap": client_to_ap,
        },
        "cpu": {
            host: {
                "total":  round(cpu["host_total"], 2),
                "user":   round(cpu["host_user"], 2),
                "system": round(cpu["host_system"], 2),
            },
            remote: {
                "total":  round(cpu["remote_total"], 2),
                "user":   round(cpu["remote_user"], 2),
                "system": round(cpu["remote_system"], 2),
            },
        },
    }

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