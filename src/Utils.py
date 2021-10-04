import glob
import os
import time
class Utils:

    def __init__(self, locale:dict) -> None:
        self.locale = locale
        pass
    def getBetween(self, startString:str, endString:str, haystack:str) -> dict:
        inBetween = ""
        try:
            inBetween = haystack.split(startString)[1].split(endString)[0]
        except IndexError:
            return {"error":self.locale["err_bad_haystack"],"success":False}
        return {"success":True, "data":inBetween}
    
    def getRegion(self) -> dict:
        logs = glob.glob(os.getenv('LOCALAPPDATA') + R'\VALORANT\Saved\Logs\*.log')
        logFileIndex = 1
        isSuccess = {"success":False}

        try:
            while not isSuccess["success"]:
                with open(logs[logFileIndex], "r", encoding="utf8") as logFile:
                    glzUrl = self.getBetween("[Session_Heartbeat], URL [POST ","session/v1/",logFile.read())
                isSuccess = glzUrl
                logFileIndex += 1
        except IndexError:
            return {"error":self.locale["err_region_failed"],"success":False}

        region = self.getBetween("https://glz-", ".", glzUrl["data"])
        shard = self.getBetween(region["data"] + ".", ".a.", glzUrl["data"])
        return {"success":True, "data":{
                                    "region":region["data"],
                                    "shard":shard["data"]}
                                    }

    def getLatestVersion(self):
        logs = glob.glob(os.getenv('LOCALAPPDATA') + R'\VALORANT\Saved\Logs\*.log')
        logFileIndex = 1
        isSuccess = {"success":False}

        try:
            while not isSuccess["success"]:
                with open(logs[logFileIndex], "r", encoding="utf8") as logFile:
                    ci_version = self.getBetween("CI server version: ", "[", logFile.read().strip())
                isSuccess = ci_version
                logFileIndex += 1
        except IndexError:
            return {"error":self.locale["err_version_failed"],"success":False}

        versionArray = ci_version["data"].split("-")
        versionArray.insert(2, "shipping")
        riotClientVersion = "-".join(versionArray).strip()
        return {"success":True, "data": riotClientVersion}

    def constructUrls(self, regionData:dict):
        return {"success":True, "data":{
                                    "pdUrl": f"https://pd.{regionData['data']['shard']}.a.pvp.net",
                                    "glzUrl": f"https://glz-{regionData['data']['region']}.{regionData['data']['shard']}.a.pvp.net",
                                    "sharedUrl": f"https://shared.{regionData['data']['shard']}.a.pvp.net"
                                    }}
    
    def isOpSuccess(self,response:dict):
        if not response["success"]:
            os.system("cls")
            print(response["error"])
            try: wait = response["cooldown"]
            except: wait = 5
            while wait != 0:
                print(wait)
                time.sleep(1)
                wait -= 1
            return False
        return True

    