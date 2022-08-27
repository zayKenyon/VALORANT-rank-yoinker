import InquirerPy
import requests
from dotenv import load_dotenv
import os
from secrets import token_urlsafe
import ssl
import yaml
import re
import json
import subprocess
import time

#temporary
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORCED_CIPHERS = [
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE+AES128',
    'RSA+AES128',
    'ECDHE+AES256',
    'RSA+AES256',
    'ECDHE+3DES',
    'RSA+3DES']

# pasted TLS from stackoverflow
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs) -> None:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.set_ciphers(':'.join(FORCED_CIPHERS))
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


class AccountManager:
    def __init__(self, log):
        self.log = log
        self.session = requests.Session()
        self.session.mount("https://", TLSAdapter())
        load_dotenv()
        self.client_names = ["rc_default", "rc_live", "rc_beta"]
        self.puuid = ""
        self.username = os.getenv("name")
        self.password = os.getenv("password")
        self.headers = {
            "Accept-Encoding": "deflate, gzip, zstd",
            "user-agent": "RiotClient/56.0.0.4578455.4552318 rso-auth (Windows;10;;Professional, x64)",
            "Cache-Control": "no-cache",
            "Accept": "application/json",
            'Accept-Language':'en-US,en;q=0.9'
        }
        self.auth_headers = {
            'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                        "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                        "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
            'X-Riot-ClientVersion': self.get_current_version(),
            "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
        }

        self.region = ""
        self.content = None
        self.pritvate_settings = os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Data\RiotGamesPrivateSettings.yaml')
        self.riot_client_path = ""
        # yaml.add_representer(str, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"'))



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
        # with open(self.pritvate_settings, "w") as f:
        #     f.write("")

    def add_account_with_client(self):
        subprocess.call("TASKKILL /F /IM RiotClientUx.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(self.pritvate_settings, "w") as f:
            f.write("")
        time.sleep(5)
        subprocess.Popen([self.riot_client_path])


    def load_account_auth(self):
        with open(self.pritvate_settings, 'r') as f:
            yaml_data = yaml.safe_load(f)
            try:
                if len(yaml_data["riot-login"]["persist"]["session"]["cookies"]) != 5:
                    # self.error(f"Account not logged in, incorrect amount of cookies, amount of cookies {len(yaml_data["riot-login"]["persist"]["session"]["cookies"])}")
                    return None
            except TypeError:
                #self.log("No cookies found in riot games private settings")
                return None
            for cookie in yaml_data["riot-login"]["persist"]["session"]["cookies"]:
                if cookie["name"] == "sub":
                    self.puuid = cookie["value"]
                cookie_name = cookie["name"]
                cookie_value = cookie["value"]
                self.session.cookies.set(cookie_name, cookie_value)
            
        data = {
            "acr_values": "",
            "claims": "",
            "client_id": "riot-client",
            "code_challenge": "",
            "code_challenge_method": "",
            "nonce": token_urlsafe(16),
            "redirect_uri": "http://localhost/redirect",
            'response_type': 'token id_token',
            "scope": "openid link ban lol_region account",
        }
        r_auth = self.session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=self.headers)
        pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
        data = pattern.findall(r_auth.json()['response']['parameters']['uri'])[0]
        access_token = data[0]
        id_token = data[1]
        expires_in = data[2]
        expire_in_epoch = int(time.time()) + int(expires_in)

        # print(r_auth.status_code)

        r_entitlements = self.session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers={'Authorization': 'Bearer ' + access_token} | self.headers, json={})
        # print(r_entitlements.status_code)
        entitlements_token = r_entitlements.json()['entitlements_token']

        self.auth_headers.update({
            'Authorization': f"Bearer {access_token}",
            'X-Riot-Entitlements-JWT': entitlements_token})
        r = requests.put("https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant", headers={'Authorization': 'Bearer ' + access_token}, json={"id_token": id_token})
        self.region = r.json()["affinities"]["live"]

        r = requests.post("https://auth.riotgames.com/userinfo", headers={'Authorization': 'Bearer ' + access_token})
        self.lol_region = r.json()["region"]["tag"]

        return {
            "cookies": self.session.cookies.get_dict(),
            "expire_in": expire_in_epoch,
            "lol_region": self.lol_region
        }
        # r = self.session.post("https://entitlements.auth.riotgames.com/api/token/v1", headers=)

    def get_account_data(self):
        #if more advande account data wants to be supported requestsV needs to be edited so it can bue used with custom headers and not lockfile
        r_mmr = requests.get(f"https://pd.{self.region}.a.pvp.net/mmr/v1/players/{self.puuid}", headers=self.auth_headers, verify=False)
        season_info = r_mmr.json()["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"].get(self.get_latest_season_id())
        if season_info is not None:
            rank = season_info["CompetitiveTier"]
        else:
            rank = 0
        rank = self.escape_ansi(NUMBERTORANKS[rank])

        name = requests.put(f"https://pd.{self.region}.a.pvp.net/name-service/v2/players", json=[self.puuid]).json()
        name = name[0]["GameName"] + "#" + name[0]["TagLine"]

        r_account_xp = requests.get(f"https://pd.{self.region}.a.pvp.net/account-xp/v1/players/{self.puuid}", headers=self.auth_headers, verify=False)
        level = r_account_xp.json()["Progress"]["Level"]
        contracts = requests.get("https://valorant-api.com/v1/contracts")
        contracts = [a for a in contracts.json()["data"] if a["content"]["relationType"] == "Season"]
        bp = contracts[-1]
        r_contracts = requests.get(f"https://pd.{self.region}.a.pvp.net/contracts/v1/contracts/{self.puuid}", headers=self.auth_headers, verify=False)
        for contract in r_contracts.json()["Contracts"]:
            if contract["ContractDefinitionID"] == bp["uuid"]:
                bp_level = contract["ProgressionLevelReached"]
        return {
            "rank": rank,
            "name": name,
            "level": level,
            "bp_level": bp_level
        }

    def get_latest_season_id(self):
        if self.content is None:
            self.content = requests.get(f"https://shared.{self.region}.a.pvp.net/content-service/v3/content", headers=self.auth_headers, verify=False)
        for season in self.content.json()["Seasons"]:
            if season["IsActive"]:
                return season["ID"]

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

    def save_account_to_config(self, authdata, data):
        self.load_accounts_config()
        self.accounts_data.update({
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
        })
        with open(os.path.join(os.getenv('APPDATA'), "vry/accounts.json"), "w") as f:
            json.dump(self.accounts_data, f)

    def test_user_pass_login(self):
        data = {
            "acr_values": "",
            "claims": "",
            "client_id": "riot-client",
            "code_challenge": "",
            "code_challenge_method": "",
            "nonce": token_urlsafe(16),
            "redirect_uri": "http://localhost/redirect",
            'response_type': 'token id_token',
            "scope": "openid link ban lol_region account",
        }
        r = self.session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=self.headers)
        print(r.text)
        print(r.status_code)
        print(self.session.cookies.get_dict())
        print()

        body = {
                    "language": "en_US",
                    "password": self.password,
                    "region": None,
                    "remember": False,
                    "type": "auth",
                    "username": self.username,
        }

        r = self.session.put("https://auth.riotgames.com/api/v1/authorization", json=body, headers=self.headers)
        print(r.text)
        print(r.status_code)
        print(self.session.cookies.get_dict())

    def get_current_version(self):
        r = requests.get("https://valorant-api.com/v1/version")
        return r.json()["data"]["riotClientVersion"]
    
    def get_riot_client_path(self):
        path = os.path.join(os.getenv("ALLUSERSPROFILE"), R'Riot Games\RiotClientInstalls.json')
        with open(path, 'r') as f:
            data = json.load(f)
        for client in self.client_names:
            if os.path.exists(data.get(client)):
                self.riot_client_path = data.get(client)
                return data.get(client)

    def escape_ansi(self, line):
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

    def menu_change_accounts(self):
        change_accounts_prompt = {
            "type": "list",
            "name": "menu",
            "message": "Please select optional features:",
            "choices": [],
        }

        add_account_prompt = {
            "type": "list",
            "name": "menu",
            "message": "Please select optional features:",
            "choices": [
                "Add account with username & password",
                "Add account by signing into riot client"
            ],
        }

        self.load_accounts_config()
        for account in self.accounts_data:
            change_accounts_prompt["choices"].append("Change to: " + self.accounts_data[account]["name"])
        change_accounts_prompt["choices"].append("Add new account")
        result = InquirerPy.prompt(change_accounts_prompt)
        if result["menu"] == "Add new account":
            result = InquirerPy.prompt(add_account_prompt)
            option = add_account_prompt["choices"].index(result["menu"])
            if option == 0:
                pass
            elif option == 1:
                self.add_account_with_client()
            
        else:
            #change to one of saved accounts
            account_name = result["menu"].split("Change to: ")[1]
            for account in self.accounts_data:
                if self.accounts_data[account]["name"] == account_name:
                    self.session.cookies.update(self.accounts_data[account]["cookies"])
                    self.switch_to_account(self.accounts_data[account])

                    auth_data = self.load_account_auth()
                    account_data = acc.get_account_data()
                    acc.save_account_to_config(auth_data, account_data)
                    acc.menu(account_data)

    def menu(self, account_data):
        if account_data is not None:
            menu_prompt = {
                "type": "list",
                "name": "menu",
                "message": "Please select optional features:",
                "choices": [
                    f"Logged in as {account_data.get('name')} | {account_data.get('rank')} | Level: {account_data.get('level')} | Battlepass {account_data.get('bp_level')}/55",
                    "Change accounts",
                    "Start Valorant"
                ],
            }
        else:
            menu_prompt = {
                "type": "list",
                "name": "menu",
                "message": "Please select optional features:",
                "choices": [
                    "Not logged in",
                    "Log in",
                ],
            }


        result = InquirerPy.prompt(menu_prompt)
        option = menu_prompt["choices"].index(result["menu"])
        if account_data != None:
            if option == 0:
                pass
            elif option == 1:
                self.menu_change_accounts()
            elif option == 2:
                subprocess.Popen([self.riot_client_path, "--launch-product=valorant", "--launch-patchline=live"])
                # subprocess.call([riot_client_path, "--launch-product=valorant", "--launch-patchline=live"])
        else:
            if option == 0:
                pass
            elif option == 1:
                self.menu_change_accounts()

    

if __name__ == "__main__":
    from constants import NUMBERTORANKS
    acc = AccountManager("a")
    acc.get_riot_client_path()
    # acc.test_new_account()
    auth_data = acc.load_account_auth()
    if auth_data is not None:
        account_data = acc.get_account_data()
        acc.save_account_to_config(auth_data, account_data)
        acc.menu(account_data)
    else:
        acc.menu(None)