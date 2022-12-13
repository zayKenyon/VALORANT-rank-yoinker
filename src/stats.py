import os
import time
import json

class Stats:
    def __init__(self):
        pass

    def save_data(self, data):
        # path = os.path.join(os.getenv('APPDATA'), R'vry\stats.json')
        try:
            os.mkdir(os.path.join(os.getenv('APPDATA'), "vry"))
        except FileExistsError:
            pass
        try:
            with open(os.path.join(os.getenv('APPDATA'), "vry/stats.json"), "r") as f:
                original_data = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            original_data = {}

        updated_data = original_data.copy()
        for puuid in data.keys():
            if original_data.get(puuid) is None:
                updated_data.update({puuid: [data[puuid]]})
            else:
                updated_data[puuid].append(data[puuid])
        
        # updated_data.update(data)
        # print(updated_data)

        with open(os.path.join(os.getenv('APPDATA'), "vry/stats.json"), "w") as f:
            json.dump(updated_data, f)
    
    def read_data(self):
        try:
            with open(os.path.join(os.getenv('APPDATA'), "vry/stats.json"), "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def convert_time(self, s):
        s = int(s)
        if s < 60:
            if s == 1:
                return f"{s} second"
            else:
                return f"{s} seconds"
        elif s < 3600:
            if s // 60 == 1:
                return f"{s // 60} minute"
            else:
                return f"{s // 60} minutes"
        elif s < 86400:
            if s // 3600 == 1:
                return f"{s // 3600} hours"
            else:
                return f"{s // 3600} hours"
        else:
            if s // 86400 == 1:
                return f"{s // 86400} days"
            else:
                return f"{s // 86400} days"