import math
import time
import requests
import json
from dateutil import parser

url = "https://api.better-call.dev/v1/contract/mainnet/KT1GWnsoFZVHGh7roXEER3qeCcgJgrXT3de2/storage"

def read_input():
    try:
        with open("outfile.json", "r+") as infile:
            input_dict = json.loads(infile.read())
    except Exception as e:
        print(f"Error: {e}")
        input_dict = {}
    return input_dict

def collect():
    try:
        parsed = requests.get(url)

        parsed_json = json.loads(parsed.text)[0]

        print(parsed_json)

        drift_timestamp_raw = parsed_json["children"][3]
        drift_timestamp = str(parser.parse(drift_timestamp_raw["value"]))

        drift_value_raw = parsed_json["children"][2]
        drift_value = drift_value_raw["value"]

        target_value_raw = parsed_json["children"][5]
        target_value = target_value_raw["value"]

        print(target_value)
        target_value_pct = round(math.exp(int(target_value) * 365 * 24 * 3600 / 2 ** 48) - 1, 10)
        print(target_value_pct)

        # e^(51410×365×24×3600÷2^48)−1
        drift_value_pct = round(math.exp(int(drift_value) * 365 * 24 * 3600 / 2 ** 48) - 1, 10)

        output_dict = {drift_timestamp: drift_value_pct}

        input_dict = read_input()

        merged = {**input_dict, **output_dict}

        print(f"Merged {input_dict} with {output_dict} into {merged}")

        with open("outfile.json", "w+") as outfile:
            outfile.write(json.dumps(merged))

    except Exception as e:
        print(f"Failed to fetch data: {e}")

if __name__ == "__main__":
    collect()