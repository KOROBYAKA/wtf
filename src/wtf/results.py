import json
from datetime import datetime
from pathlib import Path
import os

def save_json(path, final_result, metadata):

    output_file = path.joinpath("results.json")
    metadata_path = path.joinpath("metadata.json")
    with open(output_file, "w") as f:
        json.dump(final_result, f, indent=4)

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Test results are saved to {output_file}")

#depricated
def print_results(final_result, htmodes, channels, timeout):
    for channel in channels:
        ht = []
        tx_res = []
        rx_res = []
        print(f"Test channel: {channel}")
        for htmode in htmodes:
            try:
                ht.append( f" {htmode:^13} ")
                value = final_result[channel][htmode]['rx_bytes'] / (timeout * 1024)
                formatted = f"{value:.2f}kB/s"
                rx_res.append(f" {formatted:^13} ")
                value = final_result[channel][htmode]['tx_bytes'] / (timeout * 1024)
                formatted = f"{value:.2f}kB/s"
                tx_res.append(f" {formatted:^13} ")
            except Exception:
                continue
        print("HT MODE  |","|".join(ht))
        print("TX BYTES |","|".join(tx_res))
        print("RX BYTES |","|".join(rx_res))

def save_results(format, final_result, metadata):
    supported_formats = ["json"]
    if format in supported_formats:
        path = Path.cwd()
        base_dir = path.joinpath("results")
        if not base_dir.exists():
            os.mkdir(str(base_dir))
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        res_dir = base_dir.joinpath(timestamp)
        if not res_dir.exists():
            os.mkdir(str(res_dir))

        if format == "json":
            save_json(res_dir, final_result, metadata)
    else:
        raise ValueError("Supported formats: {}".format(supported_formats))

