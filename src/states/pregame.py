



class Pregame:
    def __init__(self, Requests, log):
        self.log = log

        self.Requests = Requests

        self.response = ""



    def get_pregame_match_id(self):
        global response
        try:
            response = self.Requests.fetch(url_type="glz", endpoint=f"/pregame/v1/players/{self.Requests.puuid}", method="get")
            if response.get("errorCode") == "RESOURCE_NOT_FOUND":
                return 0
            match_id = response['MatchID']
            self.log(f"retrieved pregame match id: '{match_id}'")
            return match_id
        except (KeyError, TypeError):
            self.log(f"cannot find pregame match id: {response}")
            # print(f"No match id found. {response}")
            try:
                self.response = self.Requests.fetch(url_type="glz", endpoint=f"/pregame/v1/players/{self.Requests.puuid}", method="get")
                match_id = self.response['MatchID']
                self.log(f"retrieved pregame match id: '{match_id}'")
                return match_id
            except (KeyError, TypeError):
                self.log(f"cannot find pregame match id: ")
                print(f"No match id found. {self.response}")
            return 0

    def get_pregame_stats(self):
        match_id = self.get_pregame_match_id()
        if match_id != 0:
            return self.Requests.fetch("glz", f"/pregame/v1/matches/{match_id}", "get")
        else:
            return None