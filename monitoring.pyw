import os
import json
import psutil
import re
import time
import datetime
from datetime import datetime, timedelta


def read_json_files_in_folder(folder_path):
    i = 0
    # Create an empty dictionary to hold the data
    json_data_w = {}
    
    for filename in os.listdir(folder_path):
        i += 1
        file_path = os.path.join(folder_path, filename)
        # Check if the file is a JSON file
        if filename.endswith('.json'):
            with open(file_path, 'r') as file:
                # Read and parse JSON data
                json_data_r = json.load(file)
                # Do something with the JSON data, for example print it
                monitor_path = json_data_r["monitor"]
                
                # Update the dictionary with the monitor data
                json_data_w[f"monitor{i}"] = monitor_path
    
    # Write the updated dictionary to a file
    with open("monitoring.json", "w", encoding="utf-8") as f:
        json.dump(json_data_w, f, indent=4)

folder_path = "profiles"
read_json_files_in_folder(folder_path)

def check_and_terminate_process(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            proc.terminate()


with open("monitoring.json","r", encoding="utf-8") as f:
       json_data= json.loads(f.read())
       exe_names = []
       for value in json_data.values():
       # Using regular expression to extract .exe part
        match = re.search(r'[^/]*\.exe', value)
        if match:
          exe_names.append(match.group())

while True:
 time.sleep(60)
 with open("appminder.json", "r", encoding="utf-8") as f:
    json_data = json.loads(f.read())
    ura = json_data["datetime"]

    if (ura[:10] == f"{datetime.now()}"[:10]) :
        break
    elif (ura[:10] != f"{datetime.now()}"[:10]):
        for process_name in exe_names:
          check_and_terminate_process(process_name)

