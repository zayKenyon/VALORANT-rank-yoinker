
class Rank:
    def __init__(self, Requests, log, ranks_before):
        self.Requests = Requests
        self.log = log
        self.ranks_before = ranks_before

    #in future rewrite this code
    def get_rank(self, puuid, seasonID):
        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}", "get")
        try:
            if response.ok:
                self.log("retrieved rank successfully")
                r = response.json()
                rankTIER = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["CompetitiveTier"]
                if int(rankTIER) >= 21:
                    rank = [rankTIER,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["LeaderboardRank"], ]
                elif int(rankTIER) not in (0, 1, 2, 3):
                    rank = [rankTIER,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            0,
                            ]
                else:
                    rank = [0, 0, 0]

            else:
                self.log("failed getting rank")
                self.log(response.text)
                rank = [0, 0, 0]
        except TypeError:
            rank = [0, 0, 0]
        except KeyError:
            rank = [0, 0, 0]
        max_rank = 0
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
        return [rank, response.ok]
