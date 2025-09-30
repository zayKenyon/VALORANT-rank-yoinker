import base64
import json
import time

class Presences:
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log

    def get_presence(self):
        presences = self.Requests.fetch(url_type="local", endpoint="/chat/v4/presences", method="get")
        return presences['presences']

    def get_game_state(self, presences):
        private_presence = self.get_private_presence(presences)
        if private_presence:
            return private_presence["matchPresenceData"]["sessionLoopState"]
        return None

    def get_private_presence(self, presences):
        for presence in presences:
            if presence['puuid'] == self.Requests.puuid:
                #preventing vry from crashing when lol is open
                # print(presence)
                # print(presence.get("championId"))
                if presence.get("championId") is not None or presence.get("product") == "league_of_legends":
                    return None
                else:
                    decoded_private = json.loads(base64.b64decode(presence['private']))
                    # Debug
                    # print(f"DEBUG: Decoded Private Presence -> {decoded_private}")
                    return decoded_private
        return None

    def decode_presence(self, private):
        # try:
        if "{" not in str(private) and private is not None and str(private) != "":
            dict = json.loads(base64.b64decode(str(private)).decode("utf-8"))
            if dict.get("isValid"):
                return dict
        return {
            "isValid": False,
            "partyId": 0,
            "partySize": 0,
            "partyVersion": 0,
        }

    def wait_for_presence(self, PlayersPuuids):
        while True:
            presence = self.get_presence()
            for puuid in PlayersPuuids:
                if puuid not in str(presence):
                    time.sleep(1)
                    continue
            break
