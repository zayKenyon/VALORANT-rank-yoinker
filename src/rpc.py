from pypresence import Presence
from pypresence.exceptions import DiscordNotFound, InvalidID
import nest_asyncio
import time

class Rpc():
    def __init__(self, map_dict, gamemodes, colors, log):
        nest_asyncio.apply()
        self.log = log
        self.discord_running = True
        try:
            self.rpc = Presence("1012402211134910546")
            self.rpc.connect()
            self.log("Connected to discord")
        except DiscordNotFound:
            self.log("Failed connecting to discord")
            self.discord_running = False
        self.gamemodes = gamemodes
        self.map_dict = map_dict
        self.data = {
            "agent": None,
            "rank": None,
            "rank_name": None
        }
        self.last_presence_data = {}
        self.colors = colors
        self.start_time = time.time()

    def set_data(self, data):
        self.data = self.data | data
        self.log("New data set in RPC")
        self.set_rpc(self.last_presence_data)


    def set_rpc(self, presence):
        if self.discord_running:
            try:
                if presence["isValid"]:
                    match_data = presence["matchPresenceData"]
                    party_data = presence["partyPresenceData"]
                    
                    if match_data["sessionLoopState"] == "INGAME":
                        if self.data.get("agent") is None or self.data.get("agent") == "":
                            agent_img = None
                            agent = None
                        else:
                            agent = self.colors.agent_dict.get(self.data.get("agent").lower())
                            agent_img = agent.lower().replace("/", "")

                        if presence["provisioningFlow"] == "CustomGame":
                            gamemode = "Custom Game"
                        else:
                            gamemode = self.gamemodes.get(presence['queueId'])
                        
                        details = f"{gamemode} // {presence['partyOwnerMatchScoreAllyTeam']} - {presence['partyOwnerMatchScoreEnemyTeam']}"

                        mapText = self.map_dict.get(match_data["matchMap"].lower())
                        if mapText == "The Range":
                            mapImage = "splash_range_square"
                            details = "in Range"
                            agent_img = str(self.data.get("rank"))
                            agent = self.data.get("rank_name")
                        else:
                            mapImage = f"splash_{self.map_dict.get(match_data['matchMap'].lower())}_square".lower()
                        if mapText is None or mapText == "":
                            mapText = None
                            mapImage = None

                        if self.last_presence_data.get("matchPresenceData", {}).get("sessionLoopState") != match_data["sessionLoopState"]:
                            self.start_time = time.time()

                        self.rpc.update(
                            state=f"In a Party ({party_data['partySize']} of {party_data['maxPartySize']})",
                            details=details,
                            large_image=mapImage,
                            large_text=mapText,
                            small_image=agent_img,
                            small_text=agent,
                            start=self.start_time,
                            buttons=[{"label": "What's this? 👀", "url": "https://zaykenyon.github.io/VALORANT-rank-yoinker/"}]
                        )
                        self.log("RPC in-game data update")
                    elif match_data["sessionLoopState"] == "MENUS":
                        if presence["isIdle"]:
                            image = "game_icon_yellow"
                            image_text = "VALORANT - Idle"
                        else:
                            image = "game_icon"
                            image_text = "VALORANT - Online"

                        if party_data["partyAccessibility"] == "OPEN":
                            party_string = "Open Party"
                        else:
                            party_string = "Closed Party"

                        if party_data["partyState"] == "CUSTOM_GAME_SETUP":
                            gamemode = "Custom Game"
                        else:
                            gamemode = self.gamemodes.get(presence['queueId'])

                        self.rpc.update(
                            state=f"{party_string} ({party_data['partySize']} of {party_data['maxPartySize']})",
                            details=f" Lobby - {gamemode}",
                            large_image=image,
                            large_text=image_text,
                            small_image=str(self.data.get("rank")),
                            small_text=self.data.get("rank_name"),
                            buttons=[{"label": "What's this? 👀", "url": "https://zaykenyon.github.io/VALORANT-rank-yoinker/"}]
                        )
                        self.log("RPC menu data update")
                    elif match_data["sessionLoopState"] == "PREGAME":
                        if presence["provisioningFlow"] == "CustomGame" or party_data["partyState"] == "CUSTOM_GAME_SETUP":
                            gamemode = "Custom Game"
                        else:
                            gamemode = self.gamemodes.get(presence['queueId'])

                        mapText = self.map_dict.get(match_data["matchMap"].lower())
                        mapImage = f"splash_{self.map_dict.get(match_data['matchMap'].lower())}_square".lower()
                        if mapText is None or mapText == "":
                            mapText = None
                            mapImage = None

                        self.rpc.update(
                            state=f"In a Party ({party_data['partySize']} of {party_data['maxPartySize']})",
                            details=f"Agent Select - {gamemode}",
                            large_image=mapImage,
                            large_text=mapText,
                            small_image=str(self.data.get("rank")),
                            small_text=self.data.get("rank_name"),
                            buttons=[{"label": "What's this? 👀", "url": "https://zaykenyon.github.io/VALORANT-rank-yoinker/"}]
                        )
                        self.log("RPC agent-select data update")
            except InvalidID:
                self.discord_running = False
        else:
            try:
                self.rpc = Presence("1012402211134910546")
                self.rpc.connect()
                self.discord_running = True
                self.log("Reconnected to discord")
                self.set_rpc(presence)
            except DiscordNotFound:
                self.discord_running = False
        self.last_presence_data = presence
