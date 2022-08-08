
class PlayerStats:
    def __init__(self, Requests, log, config):
        self.Requests = Requests
        self.log = log
        self.config = config

    #in future rewrite this code
    def get_stats(self, puuid):
        if not self.config.get_table_flag("headshot_percent"):
            return "N/a"

        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}/competitiveupdates?startIndex=0&endIndex=1&queue=competitive", "get")
        try:
            r = self.Requests.fetch('pd', f"/match-details/v1/matches/{response.json()['Matches'][0]['MatchID']}", "get")
            if r.status_code == 404: # too old match
                return "N/a"

            total_hits = 0
            total_headshots = 0
            for rround in r.json()["roundResults"]:
                for player in rround["playerStats"]:
                    if player["subject"] == puuid:
                        for hits in player["damage"]:
                            total_hits += hits["legshots"]
                            total_hits += hits["bodyshots"]
                            total_hits += hits["headshots"]
                            total_headshots += hits["headshots"]

            # print(f"Total hits: {total_hits}\nTotal headshots: {total_headshots}\nHS%: {round((total_headshots/total_hits)*100, 1)}")
            if total_hits == 0: # No hits
                return "N/a"
            hs = int((total_headshots/total_hits)*100)
            return hs
        except IndexError: #no matches
            return "N/a"


if __name__ == "__main__":
    from constants import version
    from requestsV import Requests
    from logs import Logging
    from errors import Error
    import urllib3
    import pyperclip
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    Logging = Logging()
    log = Logging.log

    ErrorSRC = Error(log)

    Requests = Requests(version, log, ErrorSRC)
    #custom region
    # Requests.pd_url = "https://pd.ap.a.pvp.net"

    r = PlayerStats(Requests, log)

    res = r.get_stats("")
    # print(f"Rank: {res[0][0]} - {NUMBERTORANKS[res[0][0]]}\nPeak Rank: {res[0][3]} - {NUMBERTORANKS[res[0][3]]}\nRR: {res[0][1]}\nLeaderboard: {res[0][2]}\nStatus is good: {res[1]}")
