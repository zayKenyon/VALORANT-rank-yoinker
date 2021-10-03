import requests
import json
import base64

import urllib3
from src.Utils import Utils
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Presence:
    def __init__(self, headers:dict, urls:dict, self_puuid:str) -> None:
        self.headers = headers
        self.URLs = urls
        self.self_puuid = self_puuid
        self.Utils = Utils()
        pass

    def getPresence(self):
        try:
            response = requests.get(self.URLs["localUrl"]+"/chat/v4/presences", headers=self.headers, verify=False)
            result = response.json()
        except Exception as e:
            return {"success":False, "error":e}
        return {"success":True, "data":result}

    def fetchSelfPrivate(self, presences:dict):
        try:
            selfPresence = next((player for player in presences["presences"] if player["puuid"] == self.self_puuid), False)
        except Exception as e:
            return {"success":False, "error":e}
        if not selfPresence:
            return {"success":False, "error":"Player: SELF, Not found in presences. Please enter the lobby."}
        return {"success":True, "data":selfPresence["private"]}

    def presenceDecode(self, encodedPresence:str):
        decodedPresence = base64.b64decode(encodedPresence).decode("utf-8")
        try:
            presenceDict = json.loads(decodedPresence)
            if presenceDict["isValid"]:
                return {"success":True, "data":presenceDict}
        except Exception as e:
            return {"success":False, "error": e}
        return {"success":True, "data":
                                {"isValid":False,
                                "partyId":None,
                                "partySize": None,
                                "partyVersion":None}
                                }
    
    def fetchGameState(self, decodedSelfPrivate:dict):
        try:
            loopState = decodedSelfPrivate["sessionLoopState"]
            return {"success":True, "data":loopState}
        except Exception as e:
            return {"success":False, "error": e}

    def getMatchPlayers(self, coregameStats:dict, teamId:str=None):
        players = []
        puuids = []
        try:
            for player in coregameStats["Players"]:
                puuids.append(player["Subject"])
                if teamId == None: TeamID = player["TeamID"]
                else: TeamID = teamId
                
                players.append({"Subject": player["Subject"],
                    "TeamID": TeamID,
                    "CharacterID": player["CharacterID"],
                    "AccountLevel": player["PlayerIdentity"]["AccountLevel"],
                    "Incognito":player["PlayerIdentity"]["Incognito"]})
        except Exception as e:
            return {"success":False, "error": e}
        return {"success":True, "data": {"playersData":players,"PUUIDs":puuids}}

    def getPartyFromPlayers(self, PUUIDs, presences):
        parties = {}
        for presence in presences["presences"]:
            ingame = presence["puuid"] in PUUIDs
            if not ingame:
                continue
            presenceData = self.presenceDecode(presence["private"])
            if not presenceData["success"]: return {"success":False, "error":presenceData["error"]}

            if presenceData["success"] and presenceData["data"]["isValid"]:
                if presenceData["data"]["partySize"] > 1:
                    try:
                        parties[presenceData["data"]["partyId"]].append(presence["puuid"])
                    except KeyError as e:
                        parties.update({presenceData["data"]["partyId"]:[presence["puuid"]]})
                continue
        return {"success":True, "data":parties}