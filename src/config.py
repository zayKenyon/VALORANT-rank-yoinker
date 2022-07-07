import json
from io import TextIOWrapper
from json import JSONDecodeError
import requests
import os

from src.logs import Logging

class Config:
    def __init__(self, log):
        self.log = log
        self.default = {"cooldown": 10, "weapon": "", "port": 1100, "table": {"skin": True, "rr": True, "peakrank": True, "leaderboard": True}}

        if not os.path.exists("config.json"):
            self.log("config.json not found, creating new one")
            with open("config.json", "w") as file:
                config = self.config_dialog(file)
            
        try:

            with open("config.json", "r") as file:
                self.log("config opened")
                config = json.load(file)
                keys = [k for k in config.keys()] # getting the keys in the file
                default_keys = [k for k in self.default.keys()] # getting the keys in the self.default
                missingkeys = list(filter(lambda x: x not in keys, default_keys)) # comparing the keys in the file to the keys in the default and returning the missing keys

                if len(missingkeys) > 0:
                    self.log("config.json is missing keys")
                    with open("config.json", 'w') as w:
                        self.log(f"missing keys: " + {str(missingkeys)})
                        for key in missingkeys:
                            config[key] = self.default[key]

                        self.log("Succesfully added missing keys")
                        json.dump(config, w, indent=4)


                if config.get("cooldown") is None:
                    self.log("some config values are None, getting new config")
                    config = self.config_dialog(file)

                if config.get("weapon").strip() == "":
                    weapon = input("Enter the name of the weapon you use the most (This is for tracking the skins): ").capitalize().strip()
                    self.log(f"User inputted {weapon} as the weapon")
                    with open("config.json", "w") as f:
                        if not self.weapon_check(weapon):
                            print(weapon + " is not known valorant weapon you can edit directly " + os.getcwd() + "\config.json\n")
                            config["weapon"] = "vandal"
                            json.dump(config, f, indent=4)
                            self.log("vandal weapon has been added to the config file by default")
                        else:
                            config["weapon"] = weapon
                            json.dump(config, f, indent=4)
                            self.log(f"{weapon} weapon has been added to the config file by user")
                self.table = config.get("table", {})
                
        except (JSONDecodeError):
            self.log("invalid file")
            with open("config.json", "w") as file:
                config = self.config_dialog(file)
            self.table = self.default.get("table", {})
        finally:
            self.cooldown = config["cooldown"]
            self.log(f"got cooldown with value '{self.cooldown}'")

            if not self.weapon_check(config["weapon"]):
                self.weapon = "vandal" # if the user manually entered a wrong name into the config file, this will be the default until changed by the user.
            else:   
                self.weapon = config["weapon"]
            
                

    def config_dialog(self, fileToWrite: TextIOWrapper):
        self.log("color config prompt called")
        jsonToWrite = self.default
        
        json.dump(jsonToWrite, fileToWrite)
        return jsonToWrite

    def weapon_check(self, name):
        if name in [weapon["displayName"] for weapon in requests.get("https://valorant-api.com/v1/weapons").json()["data"]]:
            return True
        else:
            return False