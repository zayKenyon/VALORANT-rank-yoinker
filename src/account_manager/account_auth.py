import requests, time, re, ssl
from secrets import token_urlsafe
from InquirerPy import prompt

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



class AccountAuth:
    def __init__(self, log, NUMBERTORANKS):
        self.log = log

        log("Getting versions from valorant-api.com for account auth-ing")
        version = self.get_current_version()

        self.session = requests.Session()
        self.session.mount("https://", TLSAdapter())
        self.headers = {
            "Accept-Encoding": "deflate, gzip, zstd",
            "user-agent": f"RiotClient/{version['riotClientBuild']} rso-auth (Windows;10;;Professional, x64)",
            "Cache-Control": "no-cache",
            "Accept": "application/json",
            'Accept-Language':'en-US,en;q=0.9'
        }
        self.auth_headers = {
            'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                        "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                        "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
            'X-Riot-ClientVersion': version["riotClientVersion"],
            "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
        }
        self.puuid = ""
        self.content = None
        self.region = ""
        self.NUMBERTORANKS = NUMBERTORANKS

    def get_current_version(self):
        return requests.get("https://valorant-api.com/v1/version").json()["data"]

        

    def auth_account(self, username=None, password=None, cookies=None):
        self.session.cookies.clear()
        if cookies != None:
            for cookie in cookies:
                self.session.cookies.set(cookie, cookies[cookie])
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
        if username == None and password == None:
            if r.json().get("response") == None:
                return None
        if username != None and password != None:
            self.log("authing with username and password")
            body = {
                        "language": "en_US",
                        "password": password,
                        "region": None,
                        "remember": True,
                        "type": "auth",
                        "username": username,
            }

            r = self.session.put("https://auth.riotgames.com/api/v1/authorization", json=body, headers=self.headers)
            #check for 2fa
            if r.json().get("type") == "multifactor":
                self.log("2fa detected")
                #get 2fa code
                body = {
                    "type": "multifactor",
                    "code": self.ask_for_mfa(),
                    "remember": True
                }
                r = self.session.put("https://auth.riotgames.com/api/v1/authorization", json=body, headers=self.headers)
            if r.json().get("error") == "auth_failure":
                return None
        pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
        data = pattern.findall(r.json()['response']['parameters']['uri'])[0]
        access_token = data[0]
        id_token = data[1]
        expires_in = data[2]
        expire_in_epoch = int(time.time()) + int(expires_in)
        r_entitlements = self.session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers={'Authorization': 'Bearer ' + access_token} | self.headers, json={})
        entitlements_token = r_entitlements.json()['entitlements_token']
        self.auth_headers.update({
            'Authorization': f"Bearer {access_token}",
            'X-Riot-Entitlements-JWT': entitlements_token})
        r = requests.put("https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant", headers={'Authorization': 'Bearer ' + access_token}, json={"id_token": id_token})
        self.region = r.json()["affinities"]["live"]
        r = requests.post("https://auth.riotgames.com/userinfo", headers={'Authorization': 'Bearer ' + access_token})
        self.lol_region = r.json()["region"]["tag"]

        self.puuid = self.session.cookies.get_dict()["sub"]
        return {
            "cookies": self.session.cookies.get_dict(),
            "expire_in": expire_in_epoch,
            "lol_region": self.lol_region
        }
    
    def get_latest_season_id(self):
        self.log("get latest season id")
        if self.content is None:
            self.content = requests.get(f"https://shared.{self.region}.a.pvp.net/content-service/v3/content", headers=self.auth_headers, verify=False)
        for season in self.content.json()["Seasons"]:
            if season["IsActive"]:
                return season["ID"]

    def get_account_data(self):
        #if more advande account data wants to be supported requestsV needs to be edited so it can bue used with custom headers and not lockfile
        r_mmr = requests.get(f"https://pd.{self.region}.a.pvp.net/mmr/v1/players/{self.puuid}", headers=self.auth_headers, verify=False)
        if r_mmr.json()["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID") is not None:
            season_info = r_mmr.json()["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"].get(self.get_latest_season_id())
            if season_info is not None:
                rank = season_info["CompetitiveTier"]
            else:
                rank = 0
        else:
            rank = 0
        rank = self.escape_ansi(self.NUMBERTORANKS[rank])
        name = requests.put(f"https://pd.{self.region}.a.pvp.net/name-service/v2/players", headers=self.auth_headers, json=[self.puuid]).json()
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

    def escape_ansi(self, line):
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

    def ask_for_mfa(self):
        self.log("asking for mfa")
        return prompt({"type": "input", "message": "Please enter your MFA/2FA code:", "name": "mfa"})["mfa"]