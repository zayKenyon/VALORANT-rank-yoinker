from prettytable import PrettyTable
from src.Cosmetics.Colors import Colors

class Tables:
    def __init__(self, selfpuuid:str, agent_dict:dict, config:dict, locale:dict) -> None:
        self.config = config
        self.locale = locale
        self.table = PrettyTable()
        self.colors = Colors(config["colors"])
        self.partyIcons = {}
        self.partyCount = 0
        self.puuid = selfpuuid
        self.agent_dict = agent_dict
        pass
    
    def addRowTable(self, table: PrettyTable, args: list):
        table.add_rows([args])

    def renderPlayers(self, players:list, parties:dict, teamid:str=None):
        lastTeam = "Red"
        blue = []
        red = []
        for player in players:
            if player["TeamID"] == "Blue": blue.append(player)
            else: red.append(player)
        if self.config["sortingMethod"].upper() == self.locale["sorting_rank_ascending"].upper(): 
            blue.sort(key=lambda blue: blue["MMRData"]["currentTier"], reverse=False) 
            red.sort(key=lambda red: red["MMRData"]["currentTier"], reverse=False)
        if self.config["sortingMethod"].upper() == self.locale["sorting_rank_descending"].upper():
            blue.sort(key=lambda blue: blue["MMRData"]["currentTier"], reverse=True) 
            red.sort(key=lambda red: red["MMRData"]["currentTier"], reverse=True)
        if self.config["sortingMethod"].upper() == self.locale["sorting_level_ascending"].upper():
            blue.sort(key=lambda blue: blue["AccountLevel"], reverse=False)
            red.sort(key=lambda red: red["AccountLevel"], reverse=False)
        if self.config["sortingMethod"].upper() == self.locale["sorting_level_descending"].upper():
            blue.sort(key=lambda blue: blue["AccountLevel"], reverse=True)
            red.sort(key=lambda red: red["AccountLevel"], reverse=True)
            
        blue.extend(red)
        players = blue
        #players.sort(key=lambda players: players["TeamID"], reverse=True)
        for player in players:
            partyIcon = "-"
            for party in parties["data"]:
                if player["Subject"] in parties["data"][party]:
                    if party not in self.partyIcons:
                        if not self.config["colors"]: 
                            partyIcon = self.colors.partyIcon
                            self.partyIcons.update({party:partyIcon})
                        else:
                            partyIcon = self.colors.partyIcons[self.partyCount]
                            self.partyIcons.update({party:partyIcon})
                        self.partyCount += 1
                    else: partyIcon = self.partyIcons[party]
                else: continue
            if teamid == None:
                TeamID = player["TeamID"]
            else: TeamID = teamid
            if TeamID != lastTeam: self.addRowTable(self.table, ["-", "-", "-", "-", "-", "-", "-", "-"])
            lastTeam = TeamID
            
            if self.config["respectPrivacy"] and player["Incognito"]: name = self.colors.getTeamColor(TeamID, "Hidden Name", player["Subject"], self.puuid)
            else: name = self.colors.getTeamColor(TeamID, player["GameName"], player["Subject"], self.puuid)
            
            level = self.colors.level_to_color(player["AccountLevel"])

            if player["CharacterID"] == "": agent = "Not selected"
            else: agent = str(self.agent_dict[player["CharacterID"].lower()])

            if not self.config["colors"]:
                rank = self.colors.ranks[player["MMRData"]["currentTier"]]
                peakRank = self.colors.ranks[player["MMRData"]["peakRank"]]
            else:
                rank = self.colors.rankColors[player["MMRData"]["currentTier"]]
                peakRank = self.colors.rankColors[player["MMRData"]["peakRank"]]

            rating = player["MMRData"]["rankedRating"]
            leaderBoard = player["MMRData"]["leaderBoard"]

            self.addRowTable(self.table, [partyIcon,
                                            agent,
                                            name,
                                            rank,
                                            rating,
                                            peakRank,
                                            leaderBoard,
                                            level])
        self.table.field_names = ["Party", "Agent", "Name", "Rank", "RR", "Peak Rank", "Leaderboard Position", "Level"]