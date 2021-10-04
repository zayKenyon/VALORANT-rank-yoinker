import requests
import json
import asyncio
import aiohttp
from src.Collector.Collector import Collector

class AsyncFunctions:

    def __init__(self, headers:dict, URLs:dict, locale:dict) -> None:
        self.URLs = URLs
        self.headers = headers
        self.collector = Collector(headers, URLs, locale)
        pass

    def getPlayerNames(self, playersData:list, PUUIDs:list):
        try:
            response = requests.put(self.URLs["pdUrl"]+"/name-service/v2/players", json=PUUIDs)
            result = response.json()
        except Exception as e:
            return {"success":False, "error":e}
        
        for k,playerData in enumerate(playersData):
            next(playersData[k].update({"GameName":f"{player['GameName']}#{player['TagLine']}"}) for player in result if playerData["Subject"] == player["Subject"])
        return {"success":True, "data":playersData}

    def getPlayerRanks(self, playersData:list, PUUIDs:list):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        try:
            responses = asyncio.run(self.asyncGetRank(PUUIDs))
        except Exception as e:
            return {"success":False, "error":e}
        for k,v in enumerate(playersData):
            playersData[k].update({"MMRData":responses[k]})
        
        return {"success":True, "data":playersData}

    def getMMR(self, playersData:list, activeSeason:str):
        for k,player in enumerate(playersData):
            try:
                response = asyncio.run(self.collector.getMMRData(activeSeason,player["MMRData"]))
                try:
                    playersData[k].update({"MMRData":response["data"]})
                except KeyError:
                    playersData[k].update({"MMRData":{"currentTier":0, "rankedRating":0, "leaderBoard":0, "peakRank": 0}})
            except Exception as e:
                return {"success":False, "error":e}
        return {"success":True, "data":playersData}

    async def asyncGetRank(self, PUUIDs:list):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for puuid in PUUIDs:
                cour = self.getRank(session=session, puuid=puuid)
                tasks.append(cour)
            ranks = await asyncio.gather(*tasks, return_exceptions=True)
            return ranks

    async def getRank(self, session:aiohttp.ClientSession,puuid:str) -> dict:
        url = self.URLs["pdUrl"]+f"/mmr/v1/players/{puuid}"
        resp = await session.request('GET', url=url, headers=self.headers)
        data = await resp.text()
        return json.loads(data)