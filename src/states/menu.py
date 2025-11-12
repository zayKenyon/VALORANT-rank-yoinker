class Menu:
    def __init__(self, Requests, log, presences):
        self.Requests = Requests
        self.log = log
        self.presences = presences

    def get_party_json(self, GamePlayersPuuid, presencesDICT):
        party_json = {}
        for presence in presencesDICT:
            if presence["puuid"] in GamePlayersPuuid:
                decodedPresence = self.presences.decode_presence(presence["private"])
                if decodedPresence["isValid"]:
                    
                    # Temp fix: Riot is swapping between nested and flat API structures.
                    party_size = 0
                    party_id = ""
                    if "partyPresenceData" in decodedPresence: # Check for nested structure
                        party_size = decodedPresence["partyPresenceData"]["partySize"]
                        party_id = decodedPresence["partyPresenceData"]["partyId"]
                    elif "partySize" in decodedPresence: # Check for flattened structure
                        party_size = decodedPresence["partySize"]
                        party_id = decodedPresence["partyId"]
                    else:
                        # No known structure found, log and fail
                        self.log("ERROR: Unknown presence API structure in 'get_party_json'.")
                        party_id = decodedPresence["partyPresenceData"]["partyId"]

                    if party_size > 1:
                        try:
                            party_json[party_id].append(presence["puuid"])
                        except KeyError:
                            party_json.update({party_id: [presence["puuid"]]})

        #remove non-in-game parties from with one player in game
        parties_to_delete = []
        for party in party_json:
            if len(party_json[party]) == 1:
                parties_to_delete.append(party)
        for party in parties_to_delete:
            del party_json[party]

        self.log(f"retrieved party json: {party_json}")
        return party_json

    def get_party_members(self, self_puuid, presencesDICT):
        res = []
        party_id = ""
        
        for presence in presencesDICT:
            if presence["puuid"] == self_puuid:
                decodedPresence = self.presences.decode_presence(presence["private"])
                if decodedPresence["isValid"]:
                    
                    # Temp fix: Riot is swapping between nested and flat API structures.
                    account_level = 0
                    if "partyPresenceData" in decodedPresence: # Check for nested structure
                        party_id = decodedPresence["partyPresenceData"]["partyId"]
                        account_level = decodedPresence["playerPresenceData"]["accountLevel"]
                    elif "partyId" in decodedPresence: # Check for flattened structure
                        party_id = decodedPresence["partyId"]
                        account_level = decodedPresence["accountLevel"]
                    else:
                        # No known structure found, log and fail
                        self.log("ERROR: Unknown presence API structure in 'get_party_members' (self).")
                        party_id = decodedPresence["partyPresenceData"]["partyId"]
                        
                    res.append({"Subject": presence["puuid"], "PlayerIdentity": {"AccountLevel": account_level}})
        
        # Find other party members
        for presence in presencesDICT:
            if presence["puuid"] == self_puuid:
                continue # Skip self
                
            decodedPresence = self.presences.decode_presence(presence["private"])
            if decodedPresence["isValid"]:
                
                # Temp fix: Riot is swapping between nested and flat API structures.
                current_party_id = ""
                account_level = 0
                if "partyPresenceData" in decodedPresence: # Check for nested structure
                    current_party_id = decodedPresence["partyPresenceData"]["partyId"]
                    account_level = decodedPresence["playerPresenceData"]["accountLevel"]
                elif "partyId" in decodedPresence: # Check for flattened structure
                    current_party_id = decodedPresence["partyId"]
                    account_level = decodedPresence["accountLevel"]
                else:
                    # No known structure found, log and fail
                    self.log("ERROR: Unknown presence API structure in 'get_party_members'.")
                    current_party_id = decodedPresence["partyPresenceData"]["partyId"]

                if current_party_id == party_id:
                    res.append({"Subject": presence["puuid"], "PlayerIdentity": {"AccountLevel": account_level}})
                    
        self.log(f"retrieved party members: {res}")
        return res