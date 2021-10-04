import requests

class Collector:

    def __init__(self, headers:dict, urls:dict, locale:dict) -> None:
        self.locale = locale
        self.headers = headers
        self.URLs = urls
        self.agentDict = {}
        self.activeSeason = ""
        pass

    def getContent(self):
        try:
            response = requests.get(self.URLs["sharedUrl"]+"/content-service/v2/content", headers=self.headers)
            content = response.json()
        except Exception as e:
            return {"success":False, "error":e}
        return {"success":True, "data":content}
    
    def getAgents(self, content:dict):
        agentDict = {}
        for agent in content["Characters"]:
            if "NPE" not in agent["AssetName"].upper(): agentDict[agent["ID"].lower()] = agent["Name"]
        if agentDict == {}:
            return {"success":False, "error":self.locale["err_agents_failed"]}
        self.agentDict = agentDict
        return {"success":True, "data":agentDict}

    def getActiveSeason(self, content:dict):
        seasonId = ""
        for season in content["Seasons"]:
            if season["IsActive"] and season["Type"] == "act": seasonId = season["ID"]
        if seasonId == "":
            return {"success":False, "error":self.locale["err_season_failed"]}
        self.activeSeason = seasonId
        return {"success":True, "data":seasonId}

    async def getPlayerRank(self, puuid:str):
        try:
            response = requests.get(self.URLs["pdUrl"]+f"/mmr/v1/players/{puuid}", headers=self.headers)
            content = response.json()
        except Exception as e:
            return {"success":False, "error":e}
        return {"success":True, "data":content}

    async def getMMRData(self, seasonId:str, mmr_response:dict):
        returnData = {"currentTier":0, "rankedRating":0, "leaderBoard":0, "peakRank": 0}
        self.mmrData = returnData
        rankedRating = 0
        leaderBoard = 0

        #Return Unranked if no Data
        try:
            seasonList = mmr_response["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]
            if seasonList == [] or seasonList is None:
                return {"success":True, "data":returnData}
        except KeyError as e:
            return {"success":False, "error":e}
        
        #Fetch highest rank reached.
        peakRank = 0
        for season in seasonList:
            winsByTier = seasonList[season]["WinsByTier"]
            if winsByTier is None or winsByTier == []:
                continue
            for tier in winsByTier:
                if int(tier) > peakRank: peakRank = int(tier)
        
        #compare and get RR and Leaderboard Pos
        try:
            currentTier = int(seasonList[seasonId]["CompetitiveTier"])
            if currentTier >= peakRank: peakRank = currentTier
            if currentTier not in [0, 1, 2, 3]: rankedRating = seasonList[seasonId]["RankedRating"]
            if currentTier >= 21: leaderBoard = seasonList[seasonId]["LeaderboardRank"]
        except Exception as e:
            return {"success":False, "error":e}
        
        #Return Success
        returnData.update({"currentTier":currentTier, "rankedRating":rankedRating, "leaderBoard":leaderBoard, "peakRank": peakRank})

        #Update Property
        self.mmrData = returnData
        return {"success":True, "data":returnData}