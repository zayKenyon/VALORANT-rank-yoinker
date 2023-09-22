from src.constants import tierDict
import re

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
                Teamcolor = name, (238, 77, 77)
            else:
                Teamcolor = orig_name, (238, 77, 77)
        elif team == 'Blue':
            if playerPuuid not in party_members:
                Teamcolor = name, (76, 151, 237)
            else:
                Teamcolor = orig_name, (76, 151, 237)
        else:
            Teamcolor = ''
        if playerPuuid == selfPuuid:
            Teamcolor = orig_name, (221, 224, 41)
        return Teamcolor

    def get_rgb_color_from_skin(self, skin_id, valoApiSkins):
        for skin in valoApiSkins.json()["data"]:
            if skin_id == skin["uuid"]:
                return self.tier_dict[skin["contentTierUuid"]]

    def level_to_color(self, level):
        if level >= 400:
            return level, (102, 212, 212)
        if level >= 300:
            return level, (207, 207, 76)
        if level >= 200:
            return level, (71, 71, 204)
        if level >= 100:
            return level, (241, 144, 54)
        if level < 100:
            return level, (211, 211, 211)
        return level, (255, 255, 255)

    def get_agent_from_uuid(self, agentUUID):
        agent = str(self.agent_dict.get(agentUUID))
        agent_color = self.AGENTCOLORLIST.get(agent.lower(), (46, 46, 46))
        return agent, agent_color

    def get_hs_gradient(self, number):
        try:
            number = int(number)
        except ValueError:
            return "N/a", (46, 46, 46)
        dark_red = (64, 15, 10)
        yellow = (140, 119, 11)
        green = (18, 204, 25)
        white = (255, 255, 255)
        gradients = {
            (0, 25): (dark_red, yellow),
            (25, 50): (yellow, green),
            (50, 100): (green, white)
        }
        f = []
        for gradient in gradients:
            if gradient[0] <= number <= gradient[1]:
                for rgb in range(3):
                    if gradients[gradient][0][rgb] > gradients[gradient][1][rgb]:
                        firstHigher = True
                    else:
                        firstHigher = False
                    if firstHigher:
                        offset = gradients[gradient][0][rgb] - gradients[gradient][1][rgb]
                    else:
                        offset = gradients[gradient][1][rgb] - gradients[gradient][0][rgb]
                    if firstHigher:
                        f.append(int(gradients[gradient][0][rgb] - offset * number / gradient[1]))
                    else:
                        f.append(int(offset * number / gradient[1] + gradients[gradient][0][rgb]))
                return number, tuple(f)

    def get_wr_gradient(self, number):
        try:
            number = int(number)
        except ValueError:
            return "N/a", (46, 46, 46)
        dark_red = (64, 15, 10)
        yellow = (140, 119, 11)
        green = (18, 204, 25)
        white = (255, 255, 255)
        gradients = {
            (0, 45): (dark_red, yellow),
            (45, 55): (yellow, green),
            (55, 100): (green, white)
        }
        f = []
        for gradient in gradients:
            if gradient[0] <= number <= gradient[1]:
                for rgb in range(3):
                    if gradients[gradient][0][rgb] > gradients[gradient][1][rgb]:
                        firstHigher = True
                    else:
                        firstHigher = False
                    if firstHigher:
                        offset = gradients[gradient][0][rgb] - gradients[gradient][1][rgb]
                    else:
                        offset = gradients[gradient][1][rgb] - gradients[gradient][0][rgb]
                    if firstHigher:
                        f.append(int(gradients[gradient][0][rgb] - offset * number / gradient[1]))
                    else:
                        f.append(int(offset * number / gradient[1] + gradients[gradient][0][rgb]))
                return number, tuple(f)

    def escape_ansi(self, line):
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

    def rgb_to_hex(self, rgb):
        r, g, b = rgb
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)