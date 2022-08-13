
class Rank:
    def __init__(self, Requests, log, ranks_before):
        self.Requests = Requests
        self.log = log
        self.ranks_before = ranks_before

    #in future rewrite this code
    def get_rank(self, puuid, seasonID):
        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}", "get")
        # pyperclip.copy(str(response.json()))
        try:
            if response.ok:
                # self.log("retrieved rank successfully")
                r = response.json()
                rankTIER = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["CompetitiveTier"]
                if int(rankTIER) >= 21:
                    rank = [rankTIER,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["LeaderboardRank"]]
                elif int(rankTIER) not in (0, 1, 2):
                    rank = [rankTIER,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            0]
                else:
                    rank = [0, 0, 0]

            else:
                self.log("failed getting rank")
                self.log(response.text)
                rank = [0, 0, 0]
                rankTIER = 0
        except TypeError:
            rankTIER = 0
            rank = [0, 0, 0]
        except KeyError:
            rankTIER = 0
            rank = [0, 0, 0]
        max_rank = rankTIER
        seasons = r["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID")
        if seasons is not None:
            for season in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
                if r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"] is not None:
                    for winByTier in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"]:
                        if season in self.ranks_before:
                            if int(winByTier) > 20:
                                winByTier = int(winByTier) + 3
                        if int(winByTier) > max_rank:
                            max_rank = int(winByTier)
            rank.append(max_rank)
        else:
            rank.append(max_rank)
        try:
            wins = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["NumberOfWinsWithPlacements"]
            total_games = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["NumberOfGames"]
            try:
                wr = int(wins / total_games * 100)
            except ZeroDivisionError: #no loses
                wr = 100
        except (KeyError, TypeError): #haven't played this season, #no data?
            # print("test")
            wr = "N/a"


        rank.append(wr)
        return [rank, response.ok]


if __name__ == "__main__":
    from constants import before_ascendant_seasons, version, NUMBERTORANKS
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
    # Requests.pd_url = "https://pd.na.a.pvp.net"

    #season id
    s_id = "67e373c7-48f7-b422-641b-079ace30b427" 

    r = Rank(Requests, log, before_ascendant_seasons)

    res = r.get_rank("", s_id)
    print(res)
    #[[rank, rr, leadeboard, peak rank, wr,] status]
    print(f"Rank: {res[0][0]} - {NUMBERTORANKS[res[0][0]]}\nPeak Rank: {res[0][3]} - {NUMBERTORANKS[res[0][3]]}\nRR: {res[0][1]}\nLeaderboard: {res[0][2]}\nStatus is good: {res[1]}\nWR: {res[0][4]}%")
