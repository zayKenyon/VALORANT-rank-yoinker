from colr import color
from src.constants import tierDict

class Colors:
    def __init__(self, hide_names, agent_dict):
        self.hide_names = hide_names
        self.agent_dict = agent_dict
        self.tier_dict = tierDict

    def get_color_from_team(self, team, name, playerPuuid, selfPuuid, agent=None):
        if agent is not None:
            if self.hide_names:
                if agent != "":
                    name = self.agent_dict[agent]
                else:
                    name = "Player"
        if team == 'Red':
            Teamcolor = color(name, fore=(238, 77, 77))
        elif team == 'Blue':
            Teamcolor = color(name, fore=(76, 151, 237))
        else:
            Teamcolor = ''
        if playerPuuid == selfPuuid:
            Teamcolor = color(name, fore=(221, 224, 41))
        return Teamcolor


    def get_rgb_color_from_skin(self, skin_id, valoApiSkins):
        for skin in valoApiSkins.json()["data"]:
            if skin_id == skin["uuid"]:
                return self.tier_dict[skin["contentTierUuid"]]
