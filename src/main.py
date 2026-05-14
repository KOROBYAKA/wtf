#!/usr/bin/python3

import time
from ap import Ap
import json
from datetime import datetime
from conf import load_config, build_ap
from tooling import connection_status,run_cmd

def main():
    final_result = {}

    config = load_config()
    AP = build_ap(config)
    if not AP.ap_status():
        print("Access Point software interface is disabled (check UCI)")
        exit()
    wifi_channels,ht_modes = AP.get_wifi_capabilities()
    #wifi_channels = ['1','2']
    #ht_modes = ['HT20','HT40']
    print("Starting tests")
    for channel in wifi_channels:
        final_result[channel] = {}
        for htmode in ht_modes:
            print(f"Setting channel:{channel} and htmode: {htmode}")
            AP.set_wifi_capabilities_OpenWrt(channel,htmode)
            time.sleep(5)
            skip = False
            for x in range(0,4,1):
                if AP.connection_status() and AP.ap_link_status():
                    break
                else:
                    if x == 3:
                        print(f"Reconnect tries are gone, probably AP is not capable to work on channel {channel} with htmode {htmode}.\nHint: "
                              f"if you are sure that AP is capable to work with this physical signal configuration increase the timeout time")
                        skip = True
                    else:
                        print("AP is offline, waiting for set up time")
                        time.sleep(5+x*5)
            if skip: continue
            result = AP.run_test(config["defaults"]["timeout"])
            final_result[channel][htmode] = result

    #print_results(final_result,ht_modes,wifi_channels,config["defaults"]["timeout"])
    #save_output(final_result)




if __name__ == "__main__":
    main()
