from typing import Protocol
import requests
import urllib3
import base64
import os

from src.Utils import Utils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class Auth:

    def __init__(self, lockFileDir:str=os.getenv('LOCALAPPDATA') + R'\Riot Games\Riot Client\Config\lockfile') -> None:
        self.lockFileDir = lockFileDir
        self.Utils = Utils()
        roamingDir = os.getenv('APPDATA') + R'\Rank_Yoinker'
        if not os.path.exists(roamingDir): os.mkdir(roamingDir)
        if not os.path.exists(roamingDir+R'\cache'): os.mkdir(roamingDir+R'\cache')
        self.cacheDir = roamingDir+R'\cache'
        self.roamingDir = roamingDir
        pass

    def startAuth(self):
        try:
            with open(self.lockFileDir, "r") as lockFile:
                lockFileData = lockFile.read().split(":")
        except FileNotFoundError:
            return {"error":"Please be in Lobby before running this. Re-checking in 5 seconds.", "success":False}
        self.authBasic = base64.b64encode(('riot:' + lockFileData[3]).encode()).decode()
        self.localHeaders = {"Authorization": f"Basic {self.authBasic}"}
        self.localUrl = {"localUrl":f"https://127.0.0.1:{lockFileData[2]}"}
        response = requests.get(self.localUrl["localUrl"]+"/entitlements/v1/token", headers=self.localHeaders, verify=False)
        self.tokens = response.json()
        return {"success":True}
    
    def constructHeaders(self):
        try:
            self.self_puuid = self.tokens["subject"]
        except KeyError:
            return {"error":"Please be in Lobby before running this. Re-checking in 5 seconds.", "success":False}
        self.headers = {
            "Authorization": f"Bearer {self.tokens['accessToken']}",
            'X-Riot-Entitlements-JWT': self.tokens['token'],
            'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                         "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                         "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
            'X-Riot-ClientVersion': self.Utils.getLatestVersion()["data"]
        }
        return {"success":True, "data":self.headers}