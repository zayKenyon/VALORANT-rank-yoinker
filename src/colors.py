from colr import color
from src.constants import tierDict

class Colors:
    def __init__(self, hide_names, agent_dict, AGENTCOLORLIST):
        self.hide_names = hide_names
        self.agent_dict = agent_dict
        self.tier_dict = tierDict
        self.AGENTCOLORLIST = AGENTCOLORLIST

    def get_color_from_team(self, team, name, playerPuuid, selfPuuid, agent=None, party_members=None):
        orig_name = name
        if agent is not None:
            if self.hide_names:
                if agent != "":
                    name = self.agent_dict[agent.lower()]
                else:
                    name = "Player"
        if team == 'Red':
            if playerPuuid not in party_members:
                Teamcolor = color(name, fore=(238, 77, 77))
            else:
                Teamcolor = color(orig_name, fore=(238, 77, 77))
        elif team == 'Blue':
            if playerPuuid not in party_members:
                Teamcolor = color(name, fore=(76, 151, 237))
            else:
                Teamcolor = color(orig_name, fore=(76, 151, 237))
        else:
            Teamcolor = ''
        if playerPuuid == selfPuuid:
            Teamcolor = color(orig_name, fore=(221, 224, 41))
        return Teamcolor


    def get_rgb_color_from_skin(self, skin_id, valoApiSkins):
        for skin in valoApiSkins.json()["data"]:
            if skin_id == skin["uuid"]:
                return self.tier_dict[skin["contentTierUuid"]]

    def level_to_color(self, level):
        if level >= 400:
            return color(level, fore=(0, 255, 255))
        elif level >= 300:
            return color(level, fore=(255, 255, 0))
        elif level >= 200:
            return color(level, fore=(0, 0, 255))
        elif level >= 100:
            return color(level, fore=(241, 144, 54))
        elif level < 100:
            return color(level, fore=(211, 211, 211))

    def get_agent_from_uuid(self, agentUUID):
        agent = str(self.agent_dict.get(agentUUID))
        if self.AGENTCOLORLIST.get(agent.lower()) != None:
            agent_color = self.AGENTCOLORLIST.get(agent.lower())
            return color(agent, fore=agent_color)
        else:
            return agent
