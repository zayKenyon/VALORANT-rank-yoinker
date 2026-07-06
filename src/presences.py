import base64
import json
import time

class Presences:
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log

    def get_presence(self):
        presences = self.Requests.fetch(url_type="local", endpoint="/chat/v4/presences", method="get")
        if presences is None:
            return None
        return presences['presences']

    def get_game_state(self, presences):
        private_presence = self.get_private_presence(presences)
        if isinstance(private_presence, dict):
            # Temp fix: Riot is swapping between nested and flat API structures.
            # Check for nested structure.
            if "matchPresenceData" in private_presence:
                match_data = private_presence.get("matchPresenceData")
                if isinstance(match_data, dict):
                    return match_data.get("sessionLoopState")
            # Check for flattened structure.
            elif "sessionLoopState" in private_presence:
                return private_presence.get("sessionLoopState")
            else:
                # No known structure found, log and fail
                self.log("ERROR: Unknown presence API structure in 'get_game_state'.")
                match_data = private_presence.get("matchPresenceData")
                if isinstance(match_data, dict):
                    return match_data.get("sessionLoopState")
        return None

    def get_private_presence(self, presences):
        try:
            for presence in presences:
                if presence.get('puuid') == self.Requests.puuid:
                    # preventing vry from crashing when lol is open
                    if presence.get("championId") is not None or presence.get("product") == "league_of_legends":
                        return None
                    else:
                        private_field = presence.get('private', '')
                        if not private_field:
                            return None
                        
                        if isinstance(private_field, dict):
                            return private_field
                        
                        if isinstance(private_field, str):
                            if "{" in private_field:
                                decoded = json.loads(private_field)
                            else:
                                decoded_bytes = base64.b64decode(private_field)
                                decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                                decoded = json.loads(decoded_str)
                            
                            if isinstance(decoded, str):
                                decoded = json.loads(decoded)
                            
                            if isinstance(decoded, dict):
                                return decoded
        except Exception as e:
            try:
                self.log(f"Error in get_private_presence: {e}")
            except Exception:
                pass
        return None

    def decode_presence(self, private):
        if private is not None and str(private) != "":
            try:
                # Case 1: Already a dictionary
                if isinstance(private, dict):
                    if "isValid" not in private:
                        private["isValid"] = True
                    return private

                # Case 2: It is a string
                if isinstance(private, str):
                    if "{" in private:
                        # Raw JSON string
                        decoded = json.loads(private)
                    else:
                        # Base64 encoded JSON string
                        decoded_bytes = base64.b64decode(private)
                        decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                        decoded = json.loads(decoded_str)

                    # Handle double serialization
                    if isinstance(decoded, str):
                        decoded = json.loads(decoded)

                    if isinstance(decoded, dict):
                        if decoded.get("isValid") or "partyId" in decoded or "partyPresenceData" in decoded:
                            if "isValid" not in decoded:
                                decoded["isValid"] = True
                            return decoded
            except Exception as e:
                try:
                    self.log(f"Error decoding presence: {e}")
                except Exception:
                    pass
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