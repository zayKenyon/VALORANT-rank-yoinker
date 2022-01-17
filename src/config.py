import json
from io import TextIOWrapper
from json import JSONDecodeError

from src.logs import Logging

class Config:
    def __init__(self, log):
        self.log = log
        try:
            with open("config.json", "r") as file:
                self.log("config opened")
                config = json.load(file)
                if config.get("cooldown") is None:
                    self.log("some config values are None, getting new config")
                    config = self.config_dialog(file)

                if config["weapon"] == "":
                    with open("config.json", "w") as f:
                        weapon = input("Enter the name of the weapon you use the most (This is for tracking the skins): ")
                        config["weapon"] = weapon
                        json.dump(config, f, indent=4)
                        self.log(f"{weapon} weapon has been added to the config file")
                
        except (FileNotFoundError, JSONDecodeError):
            self.log("file not found or invalid file")
            with open("config.json", "w") as file:
                config = self.config_dialog(file)
        finally:
            self.cooldown = config["cooldown"]
            self.log(f"got cooldown with value '{self.cooldown}'")

    def config_dialog(self, fileToWrite: TextIOWrapper):
        self.log("color config prompt called")
        jsonToWrite = {"cooldown": 1, "weapon":""}
        
        json.dump(jsonToWrite, fileToWrite)
        return jsonToWrite