import yaml, json, os, subprocess, time


class AccountConfig:
    def __init__(self, log):
        self.log = log
        # self.puuid = ""
        self.client_names = ["rc_default", "rc_live", "rc_beta"]
        self.pritvate_settings = os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Data\RiotGamesPrivateSettings.yaml')
        self.riot_client_path = ""

    def get_riot_client_path(self):
        path = os.path.join(os.getenv("ALLUSERSPROFILE"), R'Riot Games\RiotClientInstalls.json')
        with open(path, 'r') as f:
            data = json.load(f)
        for client in self.client_names:
            if os.path.exists(data.get(client)):
                self.riot_client_path = data.get(client)
                return data.get(client)

    def load_accounts_config(self):
        try:
            os.mkdir(os.path.join(os.getenv('APPDATA'), "vry"))
        except FileExistsError:
            pass
        try:
            with open(os.path.join(os.getenv('APPDATA'), "vry/accounts.json"), "r") as f:
                self.accounts_data = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.accounts_data = {}
        return self.accounts_data

    def load_current_account_cookies(self):
        with open(self.pritvate_settings, 'r') as f:
            yaml_data = yaml.safe_load(f)
            try:
                if len(yaml_data["riot-login"]["persist"]["session"]["cookies"]) != 5:
                    # self.log(f"Account not logged in, incorrect amount of cookies, amount of cookies {len(yaml_data["riot-login"]["persist"]["session"]["cookies"])}")
                    return None
            except TypeError:
                #self.log("No cookies found in riot games private settings")
                return None
            cookies = {}
            for cookie in yaml_data["riot-login"]["persist"]["session"]["cookies"]:
                # if cookie["name"] == "sub":
                    # self.puuid = cookie["value"]
                cookie_name = cookie["name"]
                cookie_value = cookie["value"]
                cookies.update({cookie_name: cookie_value})
            return cookies


    def create_yaml_config_file(self, account_data):

        return {
            "riot-login": {
                "persist": {
                    "region": f"""{account_data['lol_region'].upper()}""",
                    "session": {
                        "cookies": [
                            {
                                "domain": "riotgames.com",
                                "hostOnly": False,
                                "httpOnly": True,
                                "name": "tdid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": account_data["cookies"]["tdid"]
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": True,
                                "name": "ssid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": account_data["cookies"]["ssid"]
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": True,
                                "name": "clid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": account_data["cookies"]["clid"]
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": False,
                                "name": "sub",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": account_data["cookies"]["sub"]
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": False,
                                "name": "csid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": account_data["cookies"]["csid"]
                            },
                        ]
                    }
                }
            }
        }

    def save_account_to_config(self, authdata, data):
        self.load_accounts_config()
        updated_data = {
            authdata.get("cookies").get("sub"): {
                "rank": data.get("rank"),
                "name": data.get("name"),
                "level": data.get("level"),
                "bp_level": data.get("bp_level"),
                "expire_in": authdata.get("expire_in"),
                "lol_region": authdata.get("lol_region"),
                #convert to base64 maybe in future
                "cookies": {
                    "clid": authdata.get("cookies").get("clid"),
                    "csid": authdata.get("cookies").get("csid"),
                    "ssid": authdata.get("cookies").get("ssid"),
                    "sub": authdata.get("cookies").get("sub"),
                    "tdid": authdata.get("cookies").get("tdid")
                }
            }
        }
        self.accounts_data.update(updated_data)
        with open(os.path.join(os.getenv('APPDATA'), "vry/accounts.json"), "w") as f:
            json.dump(self.accounts_data, f)
        return updated_data
        
    def add_account_with_client(self):
        subprocess.call("TASKKILL /F /IM RiotClientUx.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(self.pritvate_settings, "w") as f:
            f.write("")
        time.sleep(5)
        subprocess.Popen([self.riot_client_path])
        #watchdog wait for login

    def switch_to_account(self, account_data):
        subprocess.call("TASKKILL /F /IM RiotClientUx.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(self.pritvate_settings, 'r') as f:
            yaml_data = yaml.safe_load(f)
            try:
                if len(yaml_data["riot-login"]["persist"]["session"]["cookies"]) == 5:
                    for i, cookie in enumerate(yaml_data["riot-login"]["persist"]["session"]["cookies"]):
                        yaml_data["riot-login"]["persist"]["session"]["cookies"][i]["value"] = account_data["cookies"].get(cookie["name"])
            except TypeError:
                yaml_data = self.create_yaml_config_file(account_data)
            else:
                # self.log.error(f"Account not logged in, incorrect amount of cookies, amount of cookies {len(yaml_data["riot-login"]["persist"]["session"]["cookies"])}")
                yaml_data = self.create_yaml_config_file(account_data)
                #need to create riotgamesprivatesettings.yaml file with content in it generated
        with open(self.pritvate_settings, "w") as f:
            yaml.dump(yaml_data, f)
