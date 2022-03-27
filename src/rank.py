class Rank:
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log

    def get_rank(self, puuid, seasonID):
        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}", "get")
        try:
            rank = self.calculate_rank(response, seasonID)
        except (TypeError, KeyError):
            rank = [0, 0, 0]
        max_rank = self.calculate_max(response)
        rank.append(max_rank)
        return [rank, response.ok]

    def calculate_rank(self, response, seasonID):
        if response.ok:
            self.log("retrieved rank successfully")
            r = response.json()
            p = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]
            rankTIER = int(p["CompetitiveTier"])
            if rankTIER >= 21:
                rank = [rankTIER, p["RankedRating"], p["LeaderboardRank"]]
            elif rankTIER not in (0, 1, 2, 3):
                rank = [rankTIER, p["RankedRating"], 0]
            else:
                rank = [0, 0, 0]
        else:
            self.log("failed getting rank")
            self.log(response.text)
            rank = [0, 0, 0]
        return rank

    def calculate_max(self, response):
            max_rank = 0
            r = response.json()
            if r.get("QueueSkills") is not None and r["QueueSkills"].get("competitive") is not None and r["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID") is not None:
                for season in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"].values():
                    if season.get("WinsByTier") is not None:
                        for winByTier in season["WinsByTier"]:
                            max_rank = max(max_rank, int(winByTier))
            return max_rank