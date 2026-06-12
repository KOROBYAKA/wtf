# WTF - Wi-Fi Test Framework

WTF is a Python CLI tool for automating Wi-Fi throughput tests across Wi-Fi radio settings.

At the current stage, WTF is designed for OpenWrt-based access points. It controls the AP over SSH, changes wireless settings through UCI, runs iperf3 throughput tests, and records ping-based latency data alongside throughput results.

## Why?

Manually changing Wi-Fi channel and bandwidth settings, running a test, recording the result, and repeating that cycle many times is tedious and error-prone. WTF automates that loop.

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

From PyPI:

```sh
pip install WTF
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

Results are written under `results/<timestamp>/` as JSON files.

Plot the newest result file:

```sh
wtf plot
```

Plot a specific result file or result directory:

```sh
wtf plot --path results/2026-06-12_12-00/results.json
wtf plot results/2026-06-12_12-00
```

## Roadmap
  - [ ] pip publish
  - [ ] RTT measurement
