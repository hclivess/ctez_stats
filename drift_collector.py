import math
import time
import requests
import json
from dateutil import parser


def block_start_get():
    return read_input()["last_block"]


def block_last_get():
    url_stats = "https://api.better-call.dev/v1/stats"
    stats_parsed = requests.get(url_stats)
    stats_parsed_json = json.loads(stats_parsed.text)
    for entry in stats_parsed_json:
        if entry["network"] == "mainnet":
            return entry["level"]


def read_input():
    try:
        with open("database.json", "r+") as infile:
            input_dict = json.loads(infile.read())
    except Exception as e:
        print(f"Error: {e}")
        input_dict = {}
    return input_dict


def collect(block_start=block_start_get(), block_last=block_last_get()):
    for level in range(block_start, block_last):
        print(f"Processing block {level}")
        try:
            url = f"https://api.better-call.dev/v1/contract/mainnet/KT1GWnsoFZVHGh7roXEER3qeCcgJgrXT3de2/storage?level={level}"
            # origination = 1793972

            parsed = requests.get(url)

            parsed_json = json.loads(parsed.text)[0]

            drift_timestamp_raw = parsed_json["children"][3]
            drift_timestamp = str(parser.parse(drift_timestamp_raw["value"]))

            drift_value = parsed_json["children"][2]["value"]

            target_value = parsed_json["children"][5]["value"]

            # ovens_value = parsed_json["children"][4]["value"] #only real time

            target_value_pct = round(math.exp(int(target_value) * 365 * 24 * 3600 / 2 ** 48) - 1)

            # e^(51410×365×24×3600÷2^48)−1
            drift_value_pct = round(math.exp(int(drift_value) * 365 * 24 * 3600 / 2 ** 48) - 1)

            output_dict = {level: {
                "drift": drift_value_pct,
                "timestamp": drift_timestamp,
                "target": target_value_pct,
                # "ovens": ovens_value
            }, "last_block": level}

            input_dict = read_input()

            merged = {**input_dict, **output_dict}

            with open("database.json", "w+") as outfile:
                outfile.write(json.dumps(merged))

        except Exception as e:
            print(f"Failed to fetch data: {e}")


if __name__ == "__main__":
    # block_start = 1793972
    block_start_val = block_start_get()
    block_last_val = block_last_get()

    collect(block_start=block_start_val,
            block_last=block_last_val)
