import requests

class Content():
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log
        self.content = {}

    def get_content(self):
        self.content = self.Requests.fetch("custom", f"https://shared.{self.Requests.region}.a.pvp.net/content-service/v3/content", "get")
        return self.content

    def get_latest_season_id(self, content):
        for season in content["Seasons"]:
            if season["IsActive"] and season["Type"] == "act":
                self.log(f"retrieved season id: {season['ID']}")
                return season["ID"]

    def get_previous_season_id(self, content):
        currentseason = []
        for season in content["Seasons"]:
            if season["IsActive"] and season["Type"] == "act":
                currentseason = season

        for season in content["Seasons"]:
            if currentseason["StartTime"] == season["EndTime"] and season["Type"] == "act":
                self.log(f"retrieved previous season id: {season['ID']}")
                return season["ID"]
        return None

    def get_all_agents(self):
        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()
        agent_dict = {}
        agent_dict.update({None: None})
        agent_dict.update({"": ""})
        for agent in rAgents["data"]:
            agent_dict.update({agent['uuid'].lower(): agent['displayName']})
        self.log(f"retrieved agent dict: {agent_dict}")
        return agent_dict

    def get_all_maps(self):
        """
        Requests data and assets of all maps.
        :return: JSON of all map information.
        """
        return requests.get("https://valorant-api.com/v1/maps").json()

    def get_map_urls(self, maps) -> dict:
        map_dict = {}
        map_dict.update({None: None})
        for Vmap in maps["data"]:
            map_dict.update({Vmap['mapUrl'].lower(): Vmap['displayName']})
        self.log(f"retrieved map dict: {map_dict}")
        return map_dict

    def get_map_splashes(self, val_maps) -> dict:
        """
        Iterates through all maps, pulling map names and splash screens.
        :param val_maps: JSON of all maps.
        :return: A dictionary of maps to splashes.
        """
        val_map_dict = {}
        val_map_dict.update({None: None})
        for val_map in val_maps["data"]:
            val_map_dict.update({val_map['displayName']: val_map['splash']})
        return val_map_dict

    def get_act_episode_from_act_id(self, act_id):
        final = {
            "act": None,
            "episode": None
        }

        def has_letter_and_number(text):
            """Check if text contains both letters and numbers (new format)."""
            has_letter = any(c.isalpha() for c in text)
            has_number = any(c.isdigit() for c in text)
            return has_letter and has_number

        def roman_to_int(roman):
            """Convert a Roman numeral to an integer."""
            roman_values = {
                'I': 1,
                'V': 5,
                'X': 10,
                'L': 50,
                'C': 100
            }
        
            total = 0
            prev_value = 0

            for char in reversed(roman.upper()):
                if char not in roman_values:
                    return None
            
                current_value = roman_values[char]
                if current_value < prev_value:
                    total -= current_value
                else:
                    total += current_value
                prev_value = current_value

            return total

        def parse_season_number(name):
            """Parse the season number from a name string."""
            if not name or not isinstance(name, str):
                return None

            parts = name.split()
            if not parts:
                return None

            number_part = parts[-1]
            
            # If it has a letter + number(new format), return the original value.
            if has_letter_and_number(number_part):
                return number_part.lower()

            # For episodes (using regular numbers primarily)
            if name.startswith('EPISODE'):
                try:
                    return int(number_part)
                except ValueError:
                    return roman_to_int(number_part)

            # For acts (using Roman numerals primarily)
            elif name.startswith('ACT'):
                roman_result = roman_to_int(number_part)
                if roman_result is not None:
                    return roman_result
            
                try:
                    return int(number_part)
                except ValueError:
                    return None

            return None

        # Process seasons to find act and episode
        act_found = False
        for season in self.content["Seasons"]:
            # Check for matching act ID
            if season["ID"].lower() == act_id.lower():
                act_num = parse_season_number(season["Name"])
                if act_num is not None:
                    final["act"] = act_num
                act_found = True
        
            # Find the first episode after the act
            if act_found and season["Type"] == "episode":
                episode_num = parse_season_number(season["Name"])
                if episode_num is not None:
                    final["episode"] = episode_num
                break

        return final
