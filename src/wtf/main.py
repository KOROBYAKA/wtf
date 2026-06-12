#!/usr/bin/python3
import time
from pathlib import Path
from wtf.conf import load_config, config_validation
from wtf.tooling import set_debug, get_directions
from wtf.results import save_results
from wtf.cli import get_parser, parse


def main():
    final_result = {}

    parser = get_parser()
    args = parse(parser)
    set_debug(args.debug)
    if args.command == "check-config":
        config = load_config(args.config)
        config_validation(config)
        print(f"Provided configuration file path is: {args.config}\nConfig is valid.")
        return 0

    elif args.command == "preflight":
        from wtf.ap import Ap

        config = load_config(args.config)
        config_validation(config)
        AP = Ap.build_ap(config)
        AP.set_iperf_cmd(config["iperf_args"])
        AP.ip_access_check()
        AP.set_ssh()
        if not AP.link_status():
            raise RuntimeError("link_status: False\nSome IP addresses are not available.")
        if not AP.ap_preflight_check_OpenWrt():
            raise RuntimeError("AP_PREFLIGHT_CHECK_OPENWRT didn't pass. Check the config and connectivity.")

        print("Config and setup are valid.\nCan start the test with:wtf run [-c,--debug]")

    elif args.command == "run":
        from wtf.ap import Ap

        #Configuring AccessPoint object for AP control
        final_result = {}
        config = load_config(args.config)
        AP = Ap.build_ap(config)
        AP.make_iperf_cmd(config["iperf_args"])
        directions = get_directions(config["directions"],config["execution_mode"])
        AP.ip_access_check()
        AP.set_ssh()
        if not AP.link_status():
            raise Exception("link_status: False\nSome IP addresses are not available.")
        if not AP.ap_preflight_check_OpenWrt():
            raise Exception("AP_PREFLIGHT_CHECK_OPENWRT didn't pass. Check the config and connectivity.")
        wifi_channels, ht_modes = AP.get_wifi_capabilities()

        print("Starting tests")
        for channel in wifi_channels:
            for ht_mode in ht_modes:
                channel_key = str(channel)
                htmode_key = str(ht_mode)

                final_result.setdefault(channel_key, {})
                final_result[channel_key].setdefault(htmode_key, {})
                print(f"Setting channel:{channel} and htmode: {ht_mode}")
                AP.set_wifi_capabilities_OpenWrt(channel,ht_mode)
                time.sleep(5)
                skip = False
                for x in range(0,4):
                    if AP.link_status():
                        break
                    else:
                        if x == 3:
                            print(f"Reconnect tries are gone, probably AP is not capable to work on channel {channel} with htmode {ht_mode}.\nHint: "
                                  f"if you are sure that AP is capable to work with this physical signal configuration increase the timeout time")
                            skip = True
                        else:
                            print("AP is offline, waiting for set up time")
                            time.sleep(5+x*5)
                if skip:
                    continue
                for direction, direction_flag in directions.items():
                    final_result[channel_key][htmode_key].setdefault(direction, {})
                    for transport, v in config["transport"].items():
                        if v:
                            result = AP.run_test(direction_flag, transport)
                            if result is not None:
                                final_result[channel_key][htmode_key][direction][transport] = result
                            elif result is None:
                                print(
                                    f"Skipping failed test: "
                                    f"channel={channel_key}, htmode={htmode_key}, "
                                    f"direction={direction}, transport={transport}"
                                )

        if AP.client is not None:
            AP.client.close()
        metadata = AP.generate_metadata()
        save_results(format="json",final_result=final_result,metadata=metadata)
        return 0

    elif args.command == "plot":
        from wtf.plotter import plot_file

        result_path = _resolve_plot_path(args.path_option or args.path)
        print(f"Plotting results from: {result_path}")
        plot_file(result_path)
        return 0


def _resolve_plot_path(path_arg=None):
    if path_arg:
        path = Path(path_arg)
        if path.is_dir():
            path = path / "results.json"

        if not path.exists():
            raise FileNotFoundError(f"Result file does not exist: {path}")

        if path.suffix.lower() != ".json":
            raise ValueError(f"Plot path must point to a JSON file: {path}")

        return path

    results_dir = Path.cwd() / "results"
    candidates = sorted(
        results_dir.glob("*/results.json"),
        key=lambda candidate: candidate.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise FileNotFoundError(
            f"No result files found under {results_dir}. Provide one with: wtf plot --path <results.json>"
        )

    return candidates[0]


if __name__ == "__main__":
    main()
