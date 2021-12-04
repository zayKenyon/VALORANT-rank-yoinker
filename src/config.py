import json
from io import TextIOWrapper
from json import JSONDecodeError

from src.logs import Logging

class Config:
    def __init__(self, log):
        self.log = log
        self.defaultCfg = {
            "cooldown": 1,
            "show-phantom": True,
            "show-vandal": True,
        }
        try:
            with open("config.json", "r") as file:
                self.log("config opened")
                config = json.load(file)
                missingCfg = False
                for k in self.defaultCfg:
                    if config.get(k) is None:
                        missingCfg = True
                        break
                if missingCfg:
                    self.log("some config values are None, getting new config")
                    config = self.config_dialog(file)
        except (FileNotFoundError, JSONDecodeError):
            self.log("file not found or invalid file")
            with open("config.json", "w") as file:
                config = self.config_dialog(file)
        finally:
            self.cooldown = config["cooldown"]
            self.showPhantom = config["show-phantom"]
            self.showVandal = config["show-vandal"]
            self.log(f"got cooldown with value '{self.cooldown}'")
            self.log(f"show-phantom: {self.showPhantom}")
            self.log(f"show-vandal: {self.showVandal}")

    def config_dialog(self, fileToWrite: TextIOWrapper):
        self.log("color config prompt called")        
        json.dump(self.defaultCfg, fileToWrite, indent=2)
        return self.defaultCfg