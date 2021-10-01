import os
import time
from src.Utils import Utils
from src.Auth import Auth
from src.Cosmetics.Tables import Tables
from prettytable import PrettyTable
from src.Collector.Collector import Collector
from src.Collector.MatchInfo import MatchData
from src.Collector.Presence import Presence
from src.Collector.AsyncRequests import AsyncFunctions

from alive_progress import alive_bar
class Proc:
    def __init__(self, config:dict) -> None:
        self.UtilsObj = Utils()
        self.authObj = Auth()
        self.config = config
        pass

    def init(self) -> None:
        #Auth Section and wait if error
        authenticated = False
        Authentication = self.authObj.startAuth()
        success = self.UtilsObj.isOpSuccess(Authentication)
        
        while not success and not authenticated:
            Authentication = self.authObj.startAuth()
            success = self.UtilsObj.isOpSuccess(Authentication)
            if success:
                authenticated = True
            pass
        
        #Get Shard and Region
        regionData = self.UtilsObj.getRegion()
        if not self.UtilsObj.isOpSuccess(regionData): return

        #Construct URLs and Headers
        self.URLs = self.UtilsObj.constructUrls(regionData)["data"]
        authenticated = False
        self.headers = self.authObj.constructHeaders()
        success = self.UtilsObj.isOpSuccess(self.headers)

        while not success and not authenticated:
            Authentication = self.authObj.startAuth()
            self.headers = self.authObj.constructHeaders()
            success = self.UtilsObj.isOpSuccess(self.headers)
            if success:
                authenticated = True
            pass
        self.asyncFunc = AsyncFunctions(headers=self.headers["data"],URLs=self.URLs)
        #Initialize Presence
        while True:
            
            currentState = self.refreshState()
            if currentState == None: continue
            
            if currentState["gameState"]["data"] == "MENUS":
                os.system("cls")
                print("Waiting for a game...")
                time.sleep(3)
                continue

            os.system("cls")
            while currentState["gameState"]["data"] != "INGAME":
                os.system("cls")
                with alive_bar(title='Fetching Players', bar='classic2') as bar:
                    renderedTable = self.start(currentState["presences"]["data"], currentState["gameState"]["data"])
                    bar()
                print(renderedTable)
                time.sleep(3)
                currentState = self.refreshState()
                
            os.system("cls")
            with alive_bar(title='Fetching Players', bar='classic2') as bar:
                renderedTable = self.start(currentState["presences"]["data"], currentState["gameState"]["data"])
                bar()
            print(renderedTable)
            another = input("Fetch another Data from the game? Y/N : ")

            if another.upper() == "Y": self.tableObj.table = PrettyTable()
            else:
                print("Goodbye!")
                time.sleep(3)
                exit()

    def refreshState(self):
        self.PresenceObj = Presence(headers=self.authObj.localHeaders, urls=self.authObj.localUrl, self_puuid=self.authObj.self_puuid)

        presences = self.PresenceObj.getPresence()
        if not self.UtilsObj.isOpSuccess(presences): return

        selfPrivate = self.PresenceObj.fetchSelfPrivate(presences["data"])
        if not self.UtilsObj.isOpSuccess(selfPrivate): return
    
        privateDecoded = self.PresenceObj.presenceDecode(selfPrivate["data"])
        if not self.UtilsObj.isOpSuccess(privateDecoded): return

        gameState = self.PresenceObj.fetchGameState(privateDecoded["data"])
        if not self.UtilsObj.isOpSuccess(gameState): return

        return {"presences":presences, "gameState":gameState}

    def start(self, presences, state):
        #Initialize Collector Objects
        matchAnalyzer = MatchData(headers=self.headers["data"], urls=self.URLs)
        dataFetcher = Collector(headers=self.headers["data"], urls=self.URLs)
        localFetcher = Collector(headers=self.authObj.localHeaders, urls=self.authObj.localUrl)
        #Fetch content
        self.content = dataFetcher.getContent()
        if not self.UtilsObj.isOpSuccess(self.content): return
        #Fetch Current act
        activeSeason = dataFetcher.getActiveSeason(self.content["data"])
        if not self.UtilsObj.isOpSuccess(activeSeason): return
        #Init tables
        self.tableObj = Tables(self.authObj.self_puuid, dataFetcher.getAgents(self.content["data"])["data"], self.config)
        if state == "PREGAME":
            MatchID = matchAnalyzer.getPreGame_Id(self.authObj.self_puuid)
            if not self.UtilsObj.isOpSuccess(MatchID): return
            MatchID = MatchID["data"]
            
            matchDetails = matchAnalyzer.getPreGameFromID(MatchID)
            if not self.UtilsObj.isOpSuccess(matchDetails): return
            allyTeam = matchDetails["data"]["AllyTeam"]
            matchPlayers = self.PresenceObj.getMatchPlayers(allyTeam,allyTeam["TeamID"])
            if not self.UtilsObj.isOpSuccess(matchPlayers): return

            parties = self.PresenceObj.getPartyFromPlayers(matchPlayers["data"]["PUUIDs"], presences)
            if not self.UtilsObj.isOpSuccess(parties): return

            playersWithNames = self.asyncFunc.getPlayerNames(matchPlayers["data"]["playersData"], matchPlayers["data"]["PUUIDs"])
            if not self.UtilsObj.isOpSuccess(parties): return

            #initialize playerRanks
            first_phase = self.asyncFunc.getPlayerRanks(playersWithNames["data"], matchPlayers["data"]["PUUIDs"])
            if not self.UtilsObj.isOpSuccess(first_phase): return
            
            MMRData = self.asyncFunc.getMMR(first_phase["data"], activeSeason["data"])
            if not self.UtilsObj.isOpSuccess(MMRData): return
            
            #render
            self.tableObj.table.title = f"STATUS: {state}"
            self.tableObj.renderPlayers(MMRData["data"], parties, allyTeam["TeamID"])
        
        if state == "INGAME":
            MatchID = matchAnalyzer.getCoreGame_Id(self.authObj.self_puuid)
            if not self.UtilsObj.isOpSuccess(MatchID): return
            MatchID = MatchID["data"]

            matchDetails = matchAnalyzer.getCoreGameFromID(MatchID)
            if not self.UtilsObj.isOpSuccess(matchDetails): return
            matchDetails = matchDetails["data"]

            matchPlayers = self.PresenceObj.getMatchPlayers(matchDetails)
            if not self.UtilsObj.isOpSuccess(matchPlayers): return
            
            parties = self.PresenceObj.getPartyFromPlayers(matchPlayers["data"]["PUUIDs"], presences)
            if not self.UtilsObj.isOpSuccess(parties): return

            playersWithNames = self.asyncFunc.getPlayerNames(matchPlayers["data"]["playersData"], matchPlayers["data"]["PUUIDs"])
            if not self.UtilsObj.isOpSuccess(parties): return

            #initialize playerRanks
            first_phase = self.asyncFunc.getPlayerRanks(playersWithNames["data"], matchPlayers["data"]["PUUIDs"])
            if not self.UtilsObj.isOpSuccess(first_phase): return
            
            MMRData = self.asyncFunc.getMMR(first_phase["data"], activeSeason["data"])
            if not self.UtilsObj.isOpSuccess(MMRData): return

            #render
            self.tableObj.table.title = f"STATUS: {state}"
            self.tableObj.renderPlayers(MMRData["data"], parties)
        
        return self.tableObj.table