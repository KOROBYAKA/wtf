# WTF - Wi-Fi Test Framework

WTF is a Python CLI tool for automating Wi-Fi throughput and latency tests across Wi-Fi radio settings.

At the current stage, WTF is designed for OpenWrt-based access points. It controls the AP over SSH, changes wireless settings through UCI, runs iperf3 throughput tests, records ping-based latency telemetry, and plots saved result files.

Current version: `0.2.0`

## Why?

Manually changing Wi-Fi channel and bandwidth settings, running a test, recording the result, and repeating that cycle many times is tedious and error-prone. WTF automates that loop.

## Features

- OpenWrt AP control over SSH and UCI.
- Automatic sweep over supported Wi-Fi channels and HT modes reported by `iwinfo`.
- iperf3 throughput tests for TCP and UDP.
- Traffic directions: client-to-AP, AP-to-client, and bidirectional.
- Ping telemetry before load and during iperf load.
- JSON result and metadata output.
- Plotting for throughput, RTT, and CPU load from saved result files.

## Prerequisites

- **Access point**: OpenWrt
- **Client machine**: Linux
- **Python**: 3.11+
- **Required tools**: `iperf3`, `ping`, `iw`, `iwinfo`, `uci`
- **OpenWrt packages**: `iputils-ping` must be installed on the OpenWrt node because BusyBox ping does not support subsecond intervals.
- **Network setup**:
  - a control network for SSH/UCI access;
  - a Wi-Fi test network for throughput and latency measurements.

## Installation

From PyPI, after the package is published:

```sh
pip install wtf
```

From source:

```sh
git clone https://github.com/KOROBYAKA/wtf
cd wtf
python3 -m venv .venv
. .venv/bin/activate
pip install .
```

For development:

```sh
pip install ".[dev]"
```

## Configuration

Create a config file from the example:

```sh
cp conf.toml.example conf.toml
```

Set the control-plane and Wi-Fi test-plane IP addresses, OpenWrt wireless identifiers, enabled directions, enabled transports, iperf settings, and ping frequency.

Execution mode controls where WTF itself is running:

```toml
# 0: WTF runs on the client/controller machine
# 1: WTF runs on the AP
execution_mode = 0
```

Transport flags use `1` for enabled and `0` for disabled:

```toml
[transport]
tcp = 1
udp = 1
```

Direction flags use the same convention:

```toml
[directions]
client_to_ap = 1
ap_to_client = 1
bidirectional = 1
```

iperf and ping settings:

```toml
[iperf_args]
timeout = 15
bandwidth = 0
packet_length = 0
fragmentation = 1

[ping_args]
frequency = 10
```

`check-config` validates required sections, IP address syntax and conflicts, execution mode, direction flags, transport flags, ping frequency, and iperf timeout type.

## Usage

Validate the config:

```sh
wtf check-config --config conf.toml
```

Run setup and connectivity checks:

```sh
wtf preflight --config conf.toml
```

Run the full test sweep:

```sh
wtf run --config conf.toml
```

Results are written under `results/<timestamp>/`.

Each run writes:

- `results.json`: channel, HT mode, direction, transport, throughput, CPU, packet loss, and RTT telemetry.
- `metadata.json`: execution mode, configured AP/client addresses, wireless identifiers, and generated iperf/ping commands.

Telemetry includes:

- iperf status, duration, reverse/bidirectional flags.
- Throughput in Mbps for `ap_to_client` and `client_to_ap`.
- Host and remote CPU utilization reported by iperf3.
- Ping packet counts, packet loss, and RTT min/avg/max/mdev for both cold and loaded windows.

## Plotting

Plot a specific result file or result directory:

```sh
wtf plot --path results/2026-06-12_12-00/results.json
wtf plot results/2026-06-12_12-00
```

The plotter creates one figure per direction and transport pair. Each figure contains:

- throughput by channel and HT mode;
- RTT by channel and HT mode;
- CPU load overlay for the nodes present in the result file.

## License

WTF is licensed under the GNU Affero General Public License v3.0. See `LICENSE`.

## Roadmap

- [ ] Publish package to PyPI.
- [ ] Improve automated test coverage.
- [ ] Improve reliability and usability.
