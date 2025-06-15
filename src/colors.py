from .constants import color
from src.constants import tierDict
import re


class Colors:
    def __init__(self, hide_names, agent_dict, AGENTCOLORLIST):
        self.hide_names = hide_names
        self.agent_dict = agent_dict
        self.tier_dict = tierDict
        self.AGENTCOLORLIST = AGENTCOLORLIST

    def get_color_from_team(
        self, team, name, playerPuuid, selfPuuid, agent=None, party_members=None
    ):
        orig_name = name
        if agent is not None:
            if self.hide_names:
                if agent != "":
                    name = self.agent_dict[agent.lower()]
                else:
                    name = "Player"
        if team == "Red":
            if playerPuuid not in party_members:
                Teamcolor = color(name, fore=(238, 77, 77))
            else:
                Teamcolor = color(orig_name, fore=(238, 77, 77))
        elif team == "Blue":
            if playerPuuid not in party_members:
                Teamcolor = color(name, fore=(76, 151, 237))
            else:
                Teamcolor = color(orig_name, fore=(76, 151, 237))
        else:
            Teamcolor = ""
        if playerPuuid == selfPuuid:
            Teamcolor = color(orig_name, fore=(221, 224, 41))
        return Teamcolor

    def get_rgb_color_from_skin(self, skin_id, valoApiSkins):
        for skin in valoApiSkins.json()["data"]:
            if skin_id == skin["uuid"]:
                return self.tier_dict[skin["contentTierUuid"]]

    def level_to_color(self, level):
        if level >= 400:
            return color(level, fore=(102, 212, 212))
        elif level >= 300:
            return color(level, fore=(207, 207, 76))
        elif level >= 200:
            return color(level, fore=(71, 71, 204))
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

    def get_hs_gradient(self, number):
        try:
            number = int(number)
        except ValueError:
            return color("N/a", fore=(46, 46, 46))
        dark_red = (64, 15, 10)
        yellow = (140, 119, 11)
        green = (18, 204, 25)
        white = (255, 255, 255)
        gradients = {
            (0, 25): (dark_red, yellow),
            (25, 50): (yellow, green),
            (50, 100): (green, white),
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
                        offset = (
                            gradients[gradient][0][rgb] - gradients[gradient][1][rgb]
                        )
                    else:
                        offset = (
                            gradients[gradient][1][rgb] - gradients[gradient][0][rgb]
                        )
                    if firstHigher:
                        f.append(
                            int(
                                gradients[gradient][0][rgb]
                                - offset * number / gradient[1]
                            )
                        )
                    else:
                        f.append(
                            int(
                                offset * number / gradient[1]
                                + gradients[gradient][0][rgb]
                            )
                        )
                return color(number, fore=f)

    def get_wr_gradient(self, number):
        try:
            number = int(number)
        except ValueError:
            return color("N/a", fore=(46, 46, 46))
        dark_red = (64, 15, 10)
        yellow = (140, 119, 11)
        green = (18, 204, 25)
        white = (255, 255, 255)
        gradients = {
            (0, 45): (dark_red, yellow),
            (45, 55): (yellow, green),
            (55, 100): (green, white),
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
                        offset = (
                            gradients[gradient][0][rgb] - gradients[gradient][1][rgb]
                        )
                    else:
                        offset = (
                            gradients[gradient][1][rgb] - gradients[gradient][0][rgb]
                        )
                    if firstHigher:
                        f.append(
                            int(
                                gradients[gradient][0][rgb]
                                - offset * number / gradient[1]
                            )
                        )
                    else:
                        f.append(
                            int(
                                offset * number / gradient[1]
                                + gradients[gradient][0][rgb]
                            )
                        )
                return color(number, fore=f)

    def get_rr_gradient(self, rr_value, afk_penalty):
        """Returns RR value in green if positive, red if negative, white if zero, and AFK penalty in a different color."""

        # If both values are N/A, return plain "N/A"
        if rr_value == "N/A" and afk_penalty == "N/A":
            return color("N/A", fore=(46, 46, 46))  # Grey for "N/A"

        try:
            rr_value = int(rr_value)
            afk_penalty = int(afk_penalty)
        except ValueError:
            return color("N/A", fore=(46, 46, 46))  # Grey for invalid values

        # Color coding for RR
        if rr_value > 0:
            rr_colored = color(
                f"+{rr_value}", fore=(18, 204, 25)
            )  # Green for positive RR
        elif rr_value < 0:
            rr_colored = color(f"{rr_value}", fore=(241, 39, 39))  # Red for negative RR
        else:
            rr_colored = color(f"{rr_value}", fore=(255, 255, 255))  # White for zero RR

        # Color coding for AFK penalty
        if afk_penalty == 0:
            afk_colored = color(
                f"({afk_penalty})", fore=(200, 200, 200)
            )  # Grey for no penalty
        elif afk_penalty <= 5:
            afk_colored = color(
                f"({afk_penalty})", fore=(255, 165, 0)
            )  # Orange for low penalty
        else:
            afk_colored = color(
                f"({afk_penalty})", fore=(255, 0, 0)
            )  # Red for high penalty

        return f"{rr_colored} {afk_colored}"

    def escape_ansi(self, line):
        ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
        return ansi_escape.sub("", line)
