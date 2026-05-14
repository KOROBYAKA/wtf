import json
from datetime import datetime

def save_output(final_result):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"test_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(final_result, f, indent=4)

    print(f"Saved test results to {output_file}")

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
            except:
                continue
        print("HT MODE  |","|".join(ht))
        print("TX BYTES |","|".join(tx_res))
        print("RX BYTES |","|".join(rx_res))