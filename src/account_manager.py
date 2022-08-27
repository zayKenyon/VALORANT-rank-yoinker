import InquirerPy
import requests
from dotenv import load_dotenv, dotenv_values
import os
from secrets import token_urlsafe
import ssl
import yaml
import re

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

        self.menu_prompt = {
            "type": "list",
            "name": "menu",
            "message": "Please select optional features:",
            "choices": [
                f"Logged in as Hamper#bad | Diamond 2 | Level 512 | Battlepass 23/55",
                "Change accounts",
                "Start Valorant"
            ],
    }

    def get_current_account(self):
        pass

    def switch_to_account(self, account):
        pass

    def load_account_data(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Data\RiotGamesPrivateSettings.yaml')
        with open(path, 'r') as f:
            yaml_data = yaml.safe_load(f)
            for cookie in yaml_data["riot-login"]["persist"]["session"]["cookies"]:
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
        print(r_auth.status_code)

        r_entitlements = self.session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers={'Authorization': 'Bearer ' + access_token} | self.headers, json={})
        print(r_entitlements.status_code)
        entitlements_token = r_entitlements['entitlements_token']

        self.auth_headers.update({
            'Authorization': f"Bearer {access_token}",
            'X-Riot-Entitlements-JWT': entitlements_token})
        # r = self.session.post("https://entitlements.auth.riotgames.com/api/token/v1", headers=)

    def test_new_account(self):
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
    
    def menu(self):
        result = InquirerPy.prompt(self.menu_prompt)
        print(self.menu_prompt["choices"].index(result["menu"]))
    

if __name__ == "__main__":
    acc = AccountManager("a")
    # acc.test_new_account()
    # acc.load_account_data()
    acc.menu()