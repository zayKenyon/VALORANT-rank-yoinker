import time
import requests

class MatchData:

    def __init__(self, headers:dict, urls:dict, locale:dict) -> None:
        self.locale = locale
        self.headers = headers
        self.URLs = urls
        pass

    def getPreGame_Id(self, puuid:str):
        printed = False
        try:
            response = requests.get(self.URLs["glzUrl"]+f"/pregame/v1/players/{puuid}", headers=self.headers)
            pregame = response.json()
            while "MatchID" not in pregame and "errorCode" not in pregame:
                if not printed:
                    print(self.locale["loading_screen"])
                    printed = True
                time.sleep(1)
                response = requests.get(self.URLs["glzUrl"]+f"/pregame/v1/players/{puuid}", headers=self.headers)
                pregame = response.json()
                if "errorCode" in pregame:
                    return {"success":True, "data":False}
        except Exception as e:
            return {"success":False, "error":e}

        matchId = pregame["MatchID"]
        return {"success":True, "data":matchId}

    def getCoreGame_Id(self, puuid:str):
        try:
            response = requests.get(self.URLs["glzUrl"]+f"/core-game/v1/players/{puuid}", headers=self.headers)
            matchId = response.json()["MatchID"]
        except Exception as e:
            return {"success":False, "error":e}
        return {"success":True, "data":matchId}

    def getCoreGameFromID(self, matchId:str):
        try:
            response = requests.get(self.URLs["glzUrl"]+f"/core-game/v1/matches/{matchId}", headers=self.headers)
            result = response.json()
        except Exception as e:
            return {"success":False, "error":e}
        return {"success":True, "data":result}

    def getPreGameFromID(self, matchId:str):
        try:
            response = requests.get(self.URLs["glzUrl"]+f"/pregame/v1/matches/{matchId}", headers=self.headers)
            result = response.json()
        except Exception as e:
            return {"success":False, "error":e}
        return {"success":True, "data":result}