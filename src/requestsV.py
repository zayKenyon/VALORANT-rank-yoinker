import base64
import json
import time
from json.decoder import JSONDecodeError
import requests
from colr import color
import os
import shutil
import sys
import zipfile
import io
import subprocess
from requests.exceptions import ConnectionError

class Requests:
    def __init__(self, version, log, Error):
        self.Error = Error
        self.version = version
        self.headers = {}
        self.log = log


        self.lockfile = self.get_lockfile()
        self.region = self.get_region()
        self.pd_url = f"https://pd.{self.region[0]}.a.pvp.net"
        self.glz_url = f"https://glz-{self.region[1][0]}.{self.region[1][1]}.a.pvp.net"
        self.log(f"Api urls: pd_url: '{self.pd_url}', glz_url: '{self.glz_url}'")
        self.region = self.region[0]
        
        self.puuid = ''
        #fetch puuid so its avaible outside
        if not self.get_headers(init=True):
            self.log("Invalid URI format, invalid lockfile, going back to menu")
            self.get_lockfile(ignoreLockfile=True)
        

    @staticmethod
    def check_version(version, copy_run_update_script):
        # checking for latest release
        try:
            r = requests.get("https://api.github.com/repos/zayKenyon/VALORANT-rank-yoinker/releases")
        except requests.exceptions.RequestException:
            print(color("[WARNING] Unable to check for updates - skipping...", fore=(255, 165, 0)))
            return

        try:
            json_data = r.json()
            release_version = json_data[0]["tag_name"]  # get release version
            for asset in json_data[0]["assets"]:
                if "zip" in asset["content_type"]:
                        link = asset["browser_download_url"] # link for the latest release
                        break
            if float(release_version) > float(version):
                print(color("[UPDATE] New version available!", fore=(0, 255, 0)))
                if sys.argv[0][-3:] == "exe":
                    while True:
                        update_now = input(color("Would you like to update now? (Y/n): ", fore=(0, 255, 0)))
                        if update_now.lower() == "n" or update_now.lower() == "no":
                            return
                        elif update_now.lower() == "y" or update_now.lower() == "yes" or update_now == "":
                            copy_run_update_script(link)
                            os._exit(1)
                        else:
                            print('Please respond with "yes" or "no" ("y", "n") or press enter')
        except Exception:
            print(color("[WARNING] Error checking for updates - skipping...", fore=(255, 165, 0)))
            return

    @staticmethod
    def copy_run_update_script(link):
        try:
            os.mkdir(os.path.join(os.getenv('APPDATA'), "vry"))
        except FileExistsError:
            pass
        shutil.copyfile("updatescript.bat", os.path.join(os.getenv('APPDATA'), "vry", "updatescript.bat"))
        r_zip = requests.get(link, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r_zip.content))
        z.extractall(os.path.join(os.getenv('APPDATA'), "vry"))
        subprocess.Popen([os.path.join(os.getenv('APPDATA'), "vry", "updatescript.bat"), os.path.join(os.getenv('APPDATA'), "vry", ".".join(os.path.basename(link).split(".")[:-1])), os.getcwd(), os.path.join(os.getenv('APPDATA'), "vry")])

    @staticmethod
    def check_status():
        # checking status
        try:
            rStatus = requests.get(
                "https://raw.githubusercontent.com/zayKenyon/VALORANT-rank-yoinker/main/status.json")
        except requests.exceptions.RequestException:
            print(color("[WARNING] Unable to check status - skipping...", fore=(255, 165, 0)))
            return

        try:
            status_data = rStatus.json()
            if not status_data["status_good"] or status_data["print_message"]:
                status_color = (255, 0, 0) if not status_data["status_good"] else (0, 255, 0)
                print(color(status_data["message_to_display"], fore=status_color))
        except Exception:
            print(color("[WARNING] Failed processing status - skipping...", fore=(255, 165, 0)))
            return
            
    def fetch(self, url_type: str, endpoint: str, method: str, rate_limit_seconds=5):
        try:
            if url_type == "glz":
                response = requests.request(method, self.glz_url + endpoint, headers=self.get_headers(), verify=False)
                self.log(f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")

                if response.status_code == 404:
                    return response.json()

                try:
                    if response.json().get("errorCode") == "BAD_CLAIMS":
                        self.log("detected bad claims")
                        self.headers = {}
                        return self.fetch(url_type, endpoint, method)
                except JSONDecodeError:
                    pass
                if not response.ok:
                    if response.status_code == 429:
                        self.log("response not ok glz endpoint: rate limit 429")
                    else:
                        self.log("response not ok glz endpoint: " + response.text)
                    time.sleep(rate_limit_seconds+5)
                    self.headers = {}
                    self.fetch(url_type, endpoint, method)
                return response.json()
            elif url_type == "pd":
                response = requests.request(method, self.pd_url + endpoint, headers=self.get_headers(), verify=False)
                self.log(
                    f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")
                if response.status_code == 404:
                    return response

                try:
                    if response.json().get("errorCode") == "BAD_CLAIMS":
                        self.log("detected bad claims")
                        self.headers = {}
                        return self.fetch(url_type, endpoint, method)
                except JSONDecodeError:
                    pass

                if not response.ok:
                    if response.status_code == 429:
                        self.log(f"response not ok pd endpoint, rate limit 429")
                    else:
                        self.log(f"response not ok pd endpoint, {response.text}")
                    time.sleep(rate_limit_seconds+5)
                    self.headers = {}
                    return self.fetch(url_type, endpoint, method, rate_limit_seconds=rate_limit_seconds+5)
                return response
            elif url_type == "local":
                local_headers = {'Authorization': 'Basic ' + base64.b64encode(
                    ('riot:' + self.lockfile['password']).encode()).decode()}
                
                while True:
                    try:
                        response = requests.request(method, f"https://127.0.0.1:{self.lockfile['port']}{endpoint}",
                                                    headers=local_headers,
                                                    verify=False)
                        if response.json().get("errorCode") == "RPC_ERROR":
                            self.log("RPC_ERROR waiting 5 seconds")
                            time.sleep(5)
                        else:
                            break
                    except ConnectionError:
                        self.log("Connection error, retrying in 5 seconds")
                        time.sleep(5)
                if endpoint != "/chat/v4/presences":
                    self.log(
                        f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                        f" response code: {response.status_code}")
                return response.json()
            elif url_type == "custom":
                response = requests.request(method, f"{endpoint}", headers=self.get_headers(), verify=False)
                self.log(
                    f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")
                if not response.ok: self.headers = {}
                return response.json()
        except json.decoder.JSONDecodeError:
            self.log(f"JSONDecodeError in fetch function, resp.code: {response.status_code}, resp_text: '{response.text}")
            print(response)
            print(response.text)

    def get_region(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if '.a.pvp.net/account-xp/v1/' in line:
                    pd_url = line.split('.a.pvp.net/account-xp/v1/')[0].split('.')[-1]
                elif 'https://glz' in line:
                    glz_url = [(line.split('https://glz-')[1].split(".")[0]),
                               (line.split('https://glz-')[1].split(".")[1])]
                if "pd_url" in locals().keys() and "glz_url" in locals().keys():
                    self.log(f"got region from logs '{[pd_url, glz_url]}'")
                    if pd_url == "pbe":
                        return ["na", "na-1", "na"]
                    return [pd_url, glz_url]

    def get_current_version(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if 'CI server version:' in line:
                    version_without_shipping = line.split('CI server version: ')[1].strip()
                    version = version_without_shipping.split("-")
                    version.insert(2, "shipping")
                    version = "-".join(version)
                    self.log(f"got version from logs '{version}'")
                    return version

    def get_lockfile(self, ignoreLockfile=False):
        #ignoring lockfile is for when lockfile exists but it's not really valid, (local endpoints are not initialized yet)
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')
        
        if self.Error.LockfileError(path, ignoreLockfile=ignoreLockfile):
            with open(path) as lockfile:
                self.log("opened lockfile")
                data = lockfile.read().split(':')
                keys = ['name', 'PID', 'port', 'password', 'protocol']
                return dict(zip(keys, data))


    def get_headers(self, refresh=False, init=False):
        if self.headers == {} or refresh:
            try_again = True
            while try_again:
                local_headers = {'Authorization': 'Basic ' + base64.b64encode(
                    ('riot:' + self.lockfile['password']).encode()).decode()}
                try:
                    response = requests.get(f"https://127.0.0.1:{self.lockfile['port']}/entitlements/v1/token",
                                            headers=local_headers, verify=False)
                    self.log(f"https://127.0.0.1:{self.lockfile['port']}/entitlements/v1/token\n{local_headers}")
                except ConnectionError:
                    self.log(f"https://127.0.0.1:{self.lockfile['port']}/entitlements/v1/token\n{local_headers}")
                    self.log("Connection error, retrying in 1 seconds, getting new lockfile")
                    time.sleep(1)
                    self.lockfile = self.get_lockfile()
                    continue
                entitlements = response.json()
                if entitlements.get("message") == "Entitlements token is not ready yet":
                    try_again = True
                    time.sleep(1)
                elif entitlements.get("message") == "Invalid URI format":
                    self.log(f"Invalid uri format: {entitlements}")
                    if init:
                        return False
                    else:
                        try_again = True
                        time.sleep(5)
                else:
                    try_again = False

            self.puuid = entitlements['subject']
            headers = {
                'Authorization': f"Bearer {entitlements['accessToken']}",
                'X-Riot-Entitlements-JWT': entitlements['token'],
                'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                         "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                         "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
                'X-Riot-ClientVersion': self.get_current_version(),
                "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
            }
            self.headers = headers
        return self.headers
