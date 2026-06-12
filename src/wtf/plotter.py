import json
from pathlib import Path


def load_file(file_path):
    """Load a WTF JSON result file."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def plot_data(data, show=True):
    """Plot WTF result data.

    Creates one figure per direction/transport pair. Each figure contains a
    throughput plot and an RTT plot grouped by channel and HT mode.
    """
    plt = _load_matplotlib()
    grouped = _group_records(data)
    figures = []

    for (direction, transport), records in grouped.items():
        if not records:
            continue

        title = f"{transport}_{_window_direction_name(direction)}"
        x_labels = [record["label"] for record in records]
        x_values = list(range(len(records)))

        fig, axes = plt.subplots(2, 1, figsize=(max(10, len(records) * 1.2), 8), sharex=True)
        fig.canvas.manager.set_window_title(title)
        fig.suptitle(title)

        _plot_metric(
            axes[0],
            x_values,
            x_labels,
            records,
            direction,
            metric="throughput",
            title="Throughput",
            ylabel="Throughput(Mbps)",
        )
        _plot_metric(
            axes[1],
            x_values,
            x_labels,
            records,
            direction,
            metric="rtt",
            title="RTT",
            ylabel="RTT(ms)",
        )

        axes[0].tick_params(axis="x", labelbottom=True)
        axes[0].set_xlabel("Channel:HT mode")
        axes[1].set_xlabel("Channel:HT mode")
        axes[1].set_xticks(x_values)
        axes[1].set_xticklabels(x_labels, rotation=45, ha="right")
        fig.tight_layout()
        figures.append(fig)

    if show:
        plt.show()

    return figures


def plot_file(file_path, show=True):
    """Load and plot a WTF JSON result file."""
    return plot_data(load_file(file_path), show=show)


def _load_matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Plotting requires matplotlib. Install it with: pip install wtf matplotlib") from exc

    return plt


def _group_records(data):
    grouped = {}

    for channel, ht_modes in _sorted_items(data):
        if not isinstance(ht_modes, dict):
            continue

        for ht_mode, directions in _sorted_items(ht_modes):
            if not isinstance(directions, dict):
                continue

            for direction, transports in _sorted_items(directions):
                if not isinstance(transports, dict):
                    continue

                for transport, record in _sorted_items(transports):
                    if not isinstance(record, dict):
                        continue

                    grouped.setdefault((direction, transport), []).append({
                        "channel": channel,
                        "ht_mode": ht_mode,
                        "label": f"ch{channel}:{ht_mode}",
                        "record": record,
                    })

    return grouped


def _plot_metric(axis, x_values, x_labels, records, direction, metric, title, ylabel):
    if metric == "rtt":
        _plot_rtt_metric(axis, x_values, records)
    else:
        series = _throughput_series(records, direction)
        for name, values in series.items():
            axis.plot(x_values, values, marker="o", label=name)

    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.grid(True, axis="y", linestyle="--", alpha=0.35)
    axis.legend(loc="upper left")

    cpu_axis = axis.twinx()
    cpu_series = _cpu_series(records)
    for name, values in cpu_series.items():
        cpu_axis.plot(x_values, values, marker="x", linestyle="--", alpha=0.75, label=name)

    cpu_axis.set_ylim(0, 100)
    cpu_axis.set_ylabel("CPU load (%)")
    cpu_axis.legend(loc="upper right")

    axis.set_xticks(x_values)
    axis.set_xticklabels(x_labels, rotation=45, ha="right")


def _plot_rtt_metric(axis, x_values, records):
    cap_half_width = 0.08
    direction_colors = {
        "ap_to_client": "tab:blue",
        "client_to_ap": "tab:orange",
    }
    window_styles = {
        "loaded": "-",
        "cold": "--",
    }
    series_offsets = {
        ("ap_to_client", "loaded"): -0.18,
        ("ap_to_client", "cold"): -0.06,
        ("client_to_ap", "loaded"): 0.06,
        ("client_to_ap", "cold"): 0.18,
    }

    for direction in ("ap_to_client", "client_to_ap"):
        for window in ("loaded", "cold"):
            stats = []
            plot_x_values = []
            avg_x_values = []
            avg_values = []
            offset = series_offsets[(direction, window)]

            for x_value, item in zip(x_values, records):
                stat = _rtt_box_stat(item["record"], direction, window)
                if stat is None:
                    continue

                shifted_x_value = x_value + offset
                stats.append(stat)
                plot_x_values.append(shifted_x_value)
                avg_x_values.append(shifted_x_value)
                avg_values.append(stat["med"])

            if not stats:
                continue

            linestyle = window_styles[window]
            label = f"{direction} {window}"

            for index, stat in enumerate(stats):
                x_value = plot_x_values[index]
                axis.vlines(
                    x_value,
                    stat["whislo"],
                    stat["whishi"],
                    color=direction_colors[direction],
                    alpha=0.65,
                    linewidth=2.0,
                    linestyles=linestyle,
                )
                axis.hlines(
                    [stat["whislo"], stat["whishi"]],
                    x_value - cap_half_width,
                    x_value + cap_half_width,
                    color=direction_colors[direction],
                    alpha=0.65,
                    linewidth=2.0,
                    linestyles=linestyle,
                )

            axis.plot(
                avg_x_values,
                avg_values,
                color=direction_colors[direction],
                marker="o",
                linewidth=1.5,
                linestyle=linestyle,
                label=label,
            )


def _throughput_series(records, direction):
    if direction == "bidirectional":
        return {
            "ap_to_client": [_throughput_value(item["record"], "ap_to_client") for item in records],
            "client_to_ap": [_throughput_value(item["record"], "client_to_ap") for item in records],
        }

    return {
        direction: [_throughput_value(item["record"], direction) for item in records],
    }


def _throughput_value(record, direction):
    return record.get("throughput", {}).get(direction)


def _rtt_value(record, direction, statistic, window):
    value = record.get(f"{direction}_ping_result_{window}_rtt_{statistic}_ms")
    if value is not None:
        return value

    if window == "loaded":
        return record.get(f"ping_{direction}_rtt_{statistic}_ms")

    return None


def _rtt_box_stat(record, direction, window):
    min_value = _rtt_value(record, direction, "min", window)
    avg_value = _rtt_value(record, direction, "avg", window)
    max_value = _rtt_value(record, direction, "max", window)

    if min_value is None and avg_value is None and max_value is None:
        return None

    if avg_value is None:
        avg_value = _average_present_values(min_value, max_value)
    if min_value is None:
        min_value = avg_value
    if max_value is None:
        max_value = avg_value

    lower = min(min_value, avg_value, max_value)
    middle = avg_value
    upper = max(min_value, avg_value, max_value)

    return {
        "whislo": lower,
        "q1": (lower + middle) / 2,
        "med": middle,
        "q3": (middle + upper) / 2,
        "whishi": upper,
    }


def _average_present_values(*values):
    present_values = [value for value in values if value is not None]
    return sum(present_values) / len(present_values)


def _cpu_series(records):
    node_names = sorted({
        node
        for item in records
        for node in item["record"].get("cpu", {}).keys()
    })

    return {
        f"{node} CPU": [
            _scale_cpu(item["record"].get("cpu", {}).get(node, {}).get("total"))
            for item in records
        ]
        for node in node_names
    }


def _scale_cpu(value):
    if value is None:
        return None

    return max(0, min(100, value))


def _window_direction_name(direction):
    if direction == "bidirectional":
        return "bidir"

    return direction


def _sorted_items(mapping):
    return sorted(mapping.items(), key=lambda item: _sort_key(item[0]))


def _sort_key(value):
    text = str(value)
    if text.isdigit():
        return (0, int(text))

    return (1, text)
