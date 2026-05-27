#!/usr/bin/python3

import time
import argparse
from wtf.conf import load_config, check_defaults, config_validation
from wtf.tooling import connection_status
from wtf.results import print_results
from wtf.ap import Ap
from wtf.cli import get_parser, parse


def main():
    final_result = {}

    parser = get_parser()
    args = parse(parser)
    if args.command == "check-config":
        config = load_config(args.config)
        config_validation(config)
        print(f"Provided configuration file path is: {args.config}\nConfig is valid.")
        return 0

    elif args.command == "run":
        #Configuring AccessPoint object for AP control
        config = load_config(args.config)
        AP = Ap.build_ap(config)
        AP.iperf_cmd = check_defaults(config["defaults"])
        AP.ip_access_check()
        AP.set_ssh()
        AP.ap_status()
        wifi_channels,ht_modes = AP.get_wifi_capabilities()
        #wifi_channels = ['1','2']
        #ht_modes = ['HT20','HT40']

        print("Starting tests")
        for channel in wifi_channels:
            final_result[channel] = {}
            for ht_mode in ht_modes:
                print(f"Setting channel:{channel} and htmode: {ht_mode}")
                AP.set_wifi_capabilities_OpenWrt(channel,ht_mode)
                time.sleep(5)
                skip = False
                for x in range(0,4):
                    if connection_status(AP.remote_wifi_ip, AP.local_wifi_ip) and AP.ap_link_status():
                        break
                    else:
                        if x == 3:
                            print(f"Reconnect tries are gone, probably AP is not capable to work on channel {channel} with htmode {ht_mode}.\nHint: "
                                  f"if you are sure that AP is capable to work with this physical signal configuration increase the timeout time")
                            skip = True
                        else:
                            print("AP is offline, waiting for set up time")
                            time.sleep(5+x*5)
                if skip: continue
                result = AP.run_test(config["defaults"]["timeout"])
                final_result[channel][ht_mode] = result
        if AP.client != None:
            AP.client.close()
        #print_results(final_result,ht_modes,wifi_channels,config["defaults"]["timeout"])
        #save_output(final_result)
        return 0




if __name__ == "__main__":
    main()
