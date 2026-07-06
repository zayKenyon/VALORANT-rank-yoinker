import threading

def get_estimated_remaining_time(queue_id, ally_score, enemy_score):
    try:
        ally = int(ally_score)
        enemy = int(enemy_score)
    except (ValueError, TypeError):
        return None

    queue_id = (queue_id or "").lower()
    if queue_id in ("competitive", "unrated", "custom", ""):
        target = 13
        round_duration_mins = 1.75
    elif queue_id == "swiftplay":
        target = 5
        round_duration_mins = 1.6
    elif queue_id in ("spikerush", "onefa"):
        target = 4
        round_duration_mins = 1.5
    else:
        return None

    max_score = max(ally, enemy)
    min_score = min(ally, enemy)

    if max_score >= target:
        return "0 min (Finished)"

    if max_score == 0:
        rounds_left = target * 1.3
    else:
        closeness = min_score / max_score
        rounds_left = (target - max_score) * (1 + closeness * 0.8)

    minutes_left = round(rounds_left * round_duration_mins)
    return f"~{minutes_left} min"

class PlayerStats:
    def __init__(self, Requests, log, config):
        self.Requests = Requests
        self.log = log
        self.config = config
        self.match_details_cache = {}
        self.cache_lock = threading.Lock()

    def clear_runtime_cache(self):
        """Clear transient runtime caches (safe to call on MENUS/new match)."""
        with self.cache_lock:
            self.match_details_cache.clear()

    def _ensure_weapons_loaded(self):
        if not hasattr(self, "weapon_dict") or not self.weapon_dict:
            self.weapon_dict = {}
            try:
                rWeapons = self.Requests.session.get("https://valorant-api.com/v1/weapons", timeout=3).json()
                for weapon in rWeapons.get("data", []):
                    self.weapon_dict[weapon['uuid'].lower()] = weapon['displayName']
            except Exception as e:
                self.log(f"PlayerStats: Error loading weapons: {e}")

    def _default_stats(self):
        return {
            "kd": "N/A",
            "hs": "N/A",
            "RankedRatingEarned": "N/A",
            "AFKPenalty": "N/A",
            "win_rate_last_20": "N/A",
            "avg_rr_gain": "N/A",
            "streak": "N/A",
            "fav_weapon": "N/A",
            "fav_weapon_kills": 0,
        }

    def _get_match_details_cached(self, match_id):
        """Fetch /match-details once per match_id for this runtime session."""
        if not match_id:
            return None

        with self.cache_lock:
            if match_id in self.match_details_cache:
                return self.match_details_cache[match_id]

            match_response = self.Requests.fetch(
                "pd",
                f"/match-details/v1/matches/{match_id}",
                "get",
            )

            if match_response.status_code == 404:
                return None

            try:
                match_data = match_response.json()
            except Exception:
                return None

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
                f"/mmr/v1/players/{puuid}/competitiveupdates?startIndex=0&endIndex=20&queue=competitive",
                "get",
            )
            matches = response.json().get("Matches", [])
            if not matches:
                return self._default_stats()
        except Exception as e:
            self.log(f"Error fetching competitive updates: {e}")
            return self._default_stats()

        wins = 0
        total_games = 0
        total_rr_gain = 0
        streak = 0
        streak_type = None

        for i, match in enumerate(matches):
            rr_earned = match.get("RankedRatingEarned", 0)
            if rr_earned > 0:
                wins += 1
                total_rr_gain += rr_earned
                if streak_type is None or streak_type == "win":
                    streak_type = "win"
                    if i == streak: streak += 1
            elif rr_earned < 0:
                if streak_type is None or streak_type == "loss":
                    streak_type = "loss"
                    if i == streak: streak += 1
            total_games += 1

        avg_rr_gain = round(total_rr_gain / wins, 1) if wins > 0 else 0
        win_rate_last_20 = round((wins / total_games) * 100) if total_games > 0 else 0
        
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

        return self._process_match_data(puuid, match_data, match_summary, win_rate_last_20, avg_rr_gain, streak, streak_type)

    def _process_match_data(self, puuid, match_data, match_summary, win_rate_last_20, avg_rr_gain, streak, streak_type):
        self._ensure_weapons_loaded()
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

        # Calculate favorite weapon
        fav_weapon = "N/A"
        fav_weapon_kills = 0
        kills_list = match_data.get("kills", [])
        if kills_list:
            weapon_counts = {}
            for kill in kills_list:
                if kill.get("killer") == puuid:
                    finishing_damage = kill.get("finishingDamage", {})
                    weapon_uuid = finishing_damage.get("damageItem") or finishing_damage.get("damageWeapon")
                    if weapon_uuid:
                        weapon_uuid = weapon_uuid.lower()
                        weapon_name = self.weapon_dict.get(weapon_uuid)
                        if weapon_name:
                            weapon_counts[weapon_name] = weapon_counts.get(weapon_name, 0) + 1
            if weapon_counts:
                fav_weapon = max(weapon_counts, key=weapon_counts.get)
                fav_weapon_kills = weapon_counts[fav_weapon]

        ranked_rating_earned = match_summary.get("RankedRatingEarned", "N/A")
        afk_penalty = match_summary.get("AFKPenalty", "N/A")

        # Compile final stats
        final_stats = {
            "kd": kd,
            "hs": round((total_headshots / total_hits) * 100) if total_hits else "N/A",
            "RankedRatingEarned": ranked_rating_earned,
            "AFKPenalty": afk_penalty,
            "win_rate_last_20": win_rate_last_20,
            "avg_rr_gain": avg_rr_gain,
            "streak": streak if streak_type == "win" else -streak if streak_type == "loss" else 0,
            "fav_weapon": fav_weapon,
            "fav_weapon_kills": fav_weapon_kills,
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