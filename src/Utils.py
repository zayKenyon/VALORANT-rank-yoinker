import glob
import os
import time
import json
import requests
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

    #Main script related
    def createConfig():
        print("Please remember that you can always change these values in \"config.json\" under the same folder.\n")
        defaultConfig = {"colors":False,
                                "respectPrivacy":True,
                                "sortingMethod":"DESC_LEVEL",
                                "locale":"en-US"}

        locales = []
        casedLocales = []
        localeFiles = glob.glob("./locales/*.json")          
        for k,localeCode in enumerate(localeFiles):
            localeName = localeCode.replace("./locales\\", "").replace("./locales/", "").split(".")[0]
            locales.append(localeName)
            casedLocales.append(localeName.upper())
        
        chosenLocale = None

        while chosenLocale == None:
            for k,v in enumerate(locales):
                print("["+str(k+1)+"] "+v)
            locale = input(f"Choose your locale. (Number only) : ")
            try:
                locale = locales[int(locale)-1]
            except:
                continue
            
            if locale.upper() in casedLocales:
                with open(f"./locales/{locale}.json", "r", encoding='utf-8') as localeFile:
                    chosenLocale = json.load(localeFile)
                    break
            else: print(f"Please choose one in the following: {locales}")

        sortingMethodArr = [chosenLocale["sorting_rank_ascending"],
        chosenLocale["sorting_rank_descending"],
        chosenLocale["sorting_level_ascending"],
        chosenLocale["sorting_level_descending"]]
        sortingMethod = None

        colors = input(chosenLocale["question_colors"])
        showNames = input(chosenLocale["question_names"])

        while sortingMethod == None:
            for k,v in enumerate(sortingMethodArr):
                print("["+str(k+1)+"] "+v)
            sortingMethod = input(chosenLocale["question_sorting_method"]+" : ")
            try:
                sortingMethod = sortingMethodArr[int(sortingMethod)-1]
            except:
                sortingMethod = None
                continue
        if colors[0].upper() == chosenLocale["yes_uppercase"]: defaultConfig["colors"] = True
        if showNames[0].upper() == chosenLocale["yes_uppercase"]: defaultConfig["respectPrivacy"] = False
        if sortingMethod.upper() == chosenLocale["sorting_rank_ascending"].upper(): defaultConfig["sortingMethod"] = chosenLocale["sorting_rank_ascending"].upper()
        elif sortingMethod.upper() == chosenLocale["sorting_level_ascending"].upper(): defaultConfig["sortingMethod"] = chosenLocale["sorting_level_ascending"].upper()
        elif sortingMethod.upper() == chosenLocale["sorting_rank_descending"].upper(): defaultConfig["sortingMethod"] = chosenLocale["sorting_rank_descending"].upper()
        elif sortingMethod.upper() == chosenLocale["sorting_level_descending"].upper(): defaultConfig["sortingMethod"] = chosenLocale["sorting_level_descending"].upper()
        else:
            print(chosenLocale["err_invalid_input"])
            input(chosenLocale["exit"])
            exit()

        with open("config.json", "w") as configFile:
            json.dump(defaultConfig, configFile)

    def copyLocales():
        os.mkdir("locales")
        branch = requests.get("https://api.github.com/repos/isaacKenyon/VALORANT-rank-yoinker/branches/dev")
        branchHash = branch.json()["commit"]["sha"]
        files = requests.get(f"https://api.github.com/repos/isaacKenyon/VALORANT-rank-yoinker/git/trees/{branchHash}").json()["tree"]
        localesFolder = next(folder for folder in files if folder["path"] == "locales")
        locales = requests.get(localesFolder["url"]).json()["tree"]
        for locale in locales:
            localeJson = requests.get(f"https://raw.githubusercontent.com/isaacKenyon/VALORANT-rank-yoinker/dev/locales/{locale['path']}").json()
            with open("./locales/"+locale["path"], "w") as localeFile: json.dump(localeJson, localeFile)

    