import time



class Coregame:
    def __init__(self, Requests, log):
        self.log = log

        self.Requests = Requests

        self.response = ""

    def get_coregame_match_id(self):
        try:
            self.response = self.Requests.fetch(url_type="glz", endpoint=f"/core-game/v1/players/{self.Requests.puuid}", method="get")
            match_id = self.response['MatchID']
            self.log(f"retrieved coregame match id: '{match_id}'")
            return match_id
        except (KeyError, TypeError):
            self.log(f"cannot find coregame match id: ")
            # print(f"No match id found. {self.response}")
            time.sleep(5)
            try:
                self.response = self.Requests.fetch(url_type="glz", endpoint=f"/core-game/v1/players/{self.Requests.puuid}", method="get")
                match_id = self.response['MatchID']
                self.log(f"retrieved coregame match id: '{match_id}'")
                return match_id
            except (KeyError, TypeError):
                self.log(f"cannot find coregame match id: ")
                print(f"No match id found. {self.response}")
            return 0

    def get_coregame_stats(self):
        self.match_id = self.get_coregame_match_id()
        return self.Requests.fetch(url_type="glz", endpoint=f"/core-game/v1/matches/{self.match_id}", method="get")