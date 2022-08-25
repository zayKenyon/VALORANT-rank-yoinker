from pypresence import Presence
from pypresence.exceptions import DiscordNotFound, InvalidID
import nest_asyncio
import time

class Rpc():
    def __init__(self, map_dict, gamemodes, colors):
        nest_asyncio.apply()
        self.discord_running = True
        try:
            self.rpc = Presence("1012402211134910546")
            self.rpc.connect()
        except DiscordNotFound:
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

    def set_data(self, data):
        self.data = self.data | data
        self.set_rpc(self.last_presence_data)

    def set_rpc(self, presence):
        if self.discord_running:
            try:
                if presence["isValid"]:
                    if presence["sessionLoopState"] == "INGAME":
                        if self.data.get("agent") is None:
                            agent_img = None
                            agent = None
                        else:
                            agent = self.colors.agent_dict.get(self.data.get("agent").lower())
                            agent_img = agent.lower().replace("/", "")

                        if presence["provisioningFlow"] == "CustomGame":
                            gamemode = "Custom Game"
                        else:
                            gamemode = self.gamemodes.get(presence['queueId'])
                        self.rpc.update(
                            state=f"In a Party ({presence['partySize']} of {presence['maxPartySize']})",
                            details=f"{gamemode} // {presence['partyOwnerMatchScoreAllyTeam']} - {presence['partyOwnerMatchScoreEnemyTeam']}",
                            large_image=f"splash_{self.map_dict.get(presence['matchMap'].lower()).lower()}_square",
                            large_text=self.map_dict.get(presence["matchMap"].lower()),
                            small_image=agent_img,
                            small_text=agent
                        )
                    elif presence["sessionLoopState"] == "MENUS":
                        if presence["isIdle"]:
                            image = "game_icon_yellow"
                            image_text = "VALORANT - Idle"
                        else:
                            image = "game_icon"
                            image_text = "VALORANT - Online"

                        if presence["partyAccessibility"] == "OPEN":
                            party_string = "Open Party"
                        else:
                            party_string = "Closed Party"

                        self.rpc.update(
                            state=f"{party_string} ({presence['partySize']} of {presence['maxPartySize']})",
                            details=f" Lobby - {self.gamemodes.get(presence['queueId'])}",
                            large_image=image,
                            large_text=image_text,
                            small_image=str(self.data.get("rank")),
                            small_text=self.data.get("rank_name")
                        )
                    elif presence["sessionLoopState"] == "PREGAME":
                        if presence["provisioningFlow"] == "CustomGame":
                            gamemode = "Custom Game"
                        else:
                            gamemode = self.gamemodes.get(presence['queueId'])
                        self.rpc.update(
                            state=f"In a Party ({presence['partySize']} of {presence['maxPartySize']})",
                            details=f"Agent Select - {gamemode}",
                            large_image=f"splash_{self.map_dict.get(presence['matchMap'].lower()).lower()}_square",
                            large_text=self.map_dict.get(presence["matchMap"].lower()),
                            small_image=str(self.data.get("rank")),
                            small_text=self.data.get("rank_name")
                        )
            except InvalidID:
                self.discord_running = False
        else:
            try:
                self.rpc = Presence("1012402211134910546")
                self.rpc.connect()
                self.discord_running = True
                self.set_rpc(presence)
            except DiscordNotFound:
                self.discord_running = False
        self.last_presence_data = presence