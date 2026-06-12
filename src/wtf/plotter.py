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
            ylabel="Throughput (Mbit/s)",
        )
        _plot_metric(
            axes[1],
            x_values,
            x_labels,
            records,
            direction,
            metric="rtt",
            title="RTT",
            ylabel="RTT avg (ms)",
        )

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
        raise RuntimeError("Plotting requires matplotlib. Install it with: pip install 'WTF[plot]'") from exc

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
    series = _metric_series(records, direction, metric)

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


def _metric_series(records, direction, metric):
    if direction == "bidirectional":
        return {
            "ap_to_client": [_metric_value(item["record"], "ap_to_client", metric) for item in records],
            "client_to_ap": [_metric_value(item["record"], "client_to_ap", metric) for item in records],
        }

    return {
        direction: [_metric_value(item["record"], direction, metric) for item in records],
    }


def _metric_value(record, direction, metric):
    if metric == "throughput":
        return record.get("throughput", {}).get(direction)

    return record.get(f"ping_{direction}_rtt_avg_ms")


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
