class PlayerStats:
    def __init__(self, Requests, log, config):
        self.Requests = Requests
        self.log = log
        self.config = config
        self.match_details_cache = {}

    def clear_runtime_cache(self):
        """Clear transient runtime caches (safe to call on MENUS/new match)."""
        self.match_details_cache.clear()

    def _default_stats(self):
        return {
            "kd": "N/A",
            "hs": "N/A",
            "RankedRatingEarned": "N/A",
            "AFKPenalty": "N/A",
        }

    def _get_match_details_cached(self, match_id):
        """Fetch /match-details once per match_id for this runtime session."""
        if not match_id:
            return None

        if match_id in self.match_details_cache:
            return self.match_details_cache[match_id]

        match_response = self.Requests.fetch(
            "pd",
            f"/match-details/v1/matches/{match_id}",
            "get",
        )

        if match_response.status_code == 404:
            return None

        match_data = match_response.json()
        self.match_details_cache[match_id] = match_data
        return match_data

    def get_stats(self, puuid):
        # Early exit if no stats are required
        if not self.config.get_table_flag(
            "headshot_percent"
        ) and not self.config.get_table_flag("kd"):
            return self._default_stats()

        # Fetch competitive updates
        try:
            response = self.Requests.fetch(
                "pd",
                f"/mmr/v1/players/{puuid}/competitiveupdates?startIndex=0&endIndex=1&queue=competitive",
                "get",
            )
            matches = response.json().get("Matches", [])
            if not matches:
                return self._default_stats()
        except Exception as e:
            self.log(f"Error fetching competitive updates: {e}")
            return self._default_stats()

        match_summary = matches[0]
        match_id = match_summary.get("MatchID")
        if not match_id:
            return self._default_stats()

        try:
            match_data = self._get_match_details_cached(match_id)
            if match_data is None:
                return self._default_stats()
        except Exception as e:
            self.log(f"Error fetching match details: {e}")
            return self._default_stats()

        return self._process_match_data(puuid, match_data, match_summary)

    def _process_match_data(self, puuid, match_data, match_summary):
        total_hits, total_headshots, kills, deaths = 0, 0, 0, 0

        # Extract round stats
        for rround in match_data.get("roundResults", []):
            for player in rround.get("playerStats", []):
                if player.get("subject") == puuid:
                    for hits in player.get("damage", []):
                        total_hits += (
                            hits.get("legshots", 0)
                            + hits.get("bodyshots", 0)
                            + hits.get("headshots", 0)
                        )
                        total_headshots += hits.get("headshots", 0)

        # Extract overall player stats
        for player in match_data.get("players", []):
            if player.get("subject") == puuid:
                stats = player.get("stats", {})
                kills = stats.get("kills", 0)
                deaths = stats.get("deaths", 0)
                break

        # Calculate KD
        kd = round(kills / deaths, 2) if deaths else kills

        ranked_rating_earned = match_summary.get("RankedRatingEarned", "N/A")
        afk_penalty = match_summary.get("AFKPenalty", "N/A")

        # Compile final stats
        final_stats = {
            "kd": kd,
            "hs": round((total_headshots / total_hits) * 100) if total_hits else "N/A",
            "RankedRatingEarned": ranked_rating_earned,
            "AFKPenalty": afk_penalty,
        }
        return final_stats


if __name__ == "__main__":
    from constants import version
    from requestsV import Requests
    from logs import Logging
    from errors import Error
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    Logging = Logging()
    log = Logging.log
    ErrorSRC = Error(log)
    Requests = Requests(version, log, ErrorSRC)

    player_stats = PlayerStats(Requests, log, "a")
    result = player_stats.get_stats("963ad672-61e1-537e-8449-06ece1a5ceb7")
    print(result)