import math
import time
import requests
import json
from dateutil import parser
import shutil


def block_start_get():
    try:
        start = read_input()["stats"]["last_block"]
    except:
        start = 1793972
    print(f"Start block: {start}")
    return start


def write_output(data):
    try:
        shutil.copy("database.json", "database.json.backup")
    except Exception as e:
        print(f"Backup failed: {e}")

    with open("database.json", "w+") as outfile:
        outfile.write(json.dumps(data))


def block_last_get():
    url_stats = "https://api.better-call.dev/v1/stats"
    stats_parsed = requests.get(url_stats)
    stats_parsed_json = json.loads(stats_parsed.text)
    for entry in stats_parsed_json:
        if entry["network"] == "mainnet":
            print(f"Last block: {entry['level']}")
            return entry["level"]


def read_input():
    try:
        with open("database.json", "r+") as infile:
            input_dict = json.loads(infile.read())
    except Exception as e:
        print(f"Error: {e}")
        input_dict = get_clear_dict()
    return input_dict


def get_clear_dict(dict_in={}):
    dict_in.clear()
    dict_out = {"data": {},
                "stats": {}
                }
    return dict_out


def merge_save(output_dict):
    print("Saving...")
    input_dict = read_input()

    merged_data = {**input_dict["data"], **output_dict["data"]}
    merged_stats = output_dict["stats"]

    print(f'Last block (to save): {output_dict["stats"]["last_block"]}')

    merged = {"data": merged_data, "stats": merged_stats}

    print(f"Total of {len(merged_data)} data entries")
    write_output(merged)


def collect(block_start, block_last):
    output_dict = get_clear_dict()

    print(f"Started processing range of {block_start} - {block_last}")
    for level in range(block_start, block_last + 1):  # +1 to include in range
        print(f"Processing block {level}")
        while True:
            try:
                url = f"https://api.better-call.dev/v1/contract/mainnet/KT1GWnsoFZVHGh7roXEER3qeCcgJgrXT3de2/storage?level={level}"
                # origination = 1793972

                parsed = requests.get(url)

                parsed_json = json.loads(parsed.text)[0]

                drift_timestamp_raw = parsed_json["children"][3]
                drift_timestamp = str(parser.parse(drift_timestamp_raw["value"]))

                drift_value = parsed_json["children"][2]["value"]

                target_value = parsed_json["children"][5]["value"]

                target_value_pct = math.exp(int(target_value) * 365 * 24 * 3600 / 2 ** 48) - 1

                # e^(51410×365×24×3600÷2^48)−1
                drift_value_pct = math.exp(int(drift_value) * 365 * 24 * 3600 / 2 ** 48) - 1

                output_dict["data"][level] = {
                    "drift": drift_value_pct,
                    "timestamp": drift_timestamp,
                    "target": target_value_pct}

                output_dict["stats"]["last_block"] = level

                if level % 1000 == 0:
                    merge_save(output_dict)
                    # output_dict = get_clear_dict()

                break

            except Exception as e:
                print(f"Failed: {e}")
                raise

    merge_save(output_dict)  # save at the end
    print(f"Finished processing range of {block_start} - {block_last}")


if __name__ == "__main__":
    # block_start = 1793972
    collect(block_last=block_last_get(),
            block_start=block_start_get())
