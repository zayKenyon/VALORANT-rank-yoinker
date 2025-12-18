"""
Mock Data System for VALORANT Rank Yoinker (macOS Testing)

This module provides realistic mock data for testing the application without VALORANT running.
It intercepts API calls and returns simulated responses that match the actual VALORANT API structure.

Usage:
    1. Enable mock mode in config.json: "mock_mode": true
    2. Run the application normally: python main.py
    3. The application will use mock data instead of real API calls

Custom for macOS development - does not conflict with upstream code.
"""

import json
import random
import time
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path


class MockDataGenerator:
    """Generates realistic mock data for VALORANT API responses."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize mock data generator.

        Args:
            seed: Random seed for reproducible mock data
        """
        if seed:
            random.seed(seed)

        self.current_puuid = str(uuid.uuid4())
        self.player_cache: Dict[str, Dict] = {}

        # Load mock data files
        self.mock_dir = Path(__file__).parent / "mock_data"
        self._ensure_mock_dir()

    def _ensure_mock_dir(self):
        """Create mock_data directory if it doesn't exist."""
        self.mock_dir.mkdir(exist_ok=True)

    # ==================== PLAYER DATA ====================

    def generate_player_name(self) -> Dict[str, str]:
        """Generate realistic player name."""
        first_names = [
            "Shadow", "Phantom", "Viper", "Sage", "Reyna", "Jett", "Cypher",
            "Sova", "Phoenix", "Omen", "Breach", "Raze", "Killjoy", "Neon",
            "Chamber", "Fade", "Harbor", "Gekko", "Deadlock", "Iso", "Clove"
        ]

        last_names = [
            "King", "Ace", "Pro", "Master", "Legend", "God", "Demon",
            "Ninja", "Sniper", "Clutch", "Carry", "Frag", "MVP", "Beast"
        ]

        numbers = ["", "69", "420", "187", "007", "404", "999", "13", "777"]

        first = random.choice(first_names)
        last = random.choice(last_names)
        num = random.choice(numbers)

        game_name = f"{first}{last}{num}"
        tag_line = f"{random.choice(['NA', 'EU', 'ASIA', 'BR', 'LATAM', 'KR'])}{random.randint(1, 9999):04d}"

        return {
            "GameName": game_name,
            "TagLine": tag_line,
            "Subject": str(uuid.uuid4())
        }

    def generate_rank_data(self, rank_tier: Optional[int] = None) -> Dict[str, Any]:
        """Generate rank data for a player.

        Args:
            rank_tier: Specific rank tier (0-27), or None for random

        Returns:
            Dict with rank information matching VALORANT API structure
        """
        if rank_tier is None:
            # Weight towards lower ranks (more realistic distribution)
            weights = [5, 5, 5] + [8]*3 + [10]*3 + [12]*3 + [10]*3 + [8]*3 + [6]*3 + [4]*3 + [2]*3 + [1]
            rank_tier = random.choices(range(28), weights=weights)[0]

        # Generate RR (Ranked Rating) based on rank
        if rank_tier in [0, 1, 2]:  # Unranked
            rr = 0
            leaderboard = 0
        elif rank_tier >= 21:  # Ascendant+
            rr = random.randint(10, 100)
            # 10% chance of being on leaderboard for Immortal/Radiant
            if rank_tier >= 24 and random.random() < 0.3:
                leaderboard = random.randint(1, 500)
            else:
                leaderboard = 0
        else:
            rr = random.randint(5, 95)
            leaderboard = 0

        # Peak rank (usually higher or same as current)
        peak_rank = max(rank_tier, random.randint(rank_tier, min(27, rank_tier + 6)))

        # Win rate and games played
        total_games = random.randint(10, 500)
        wins = int(total_games * random.uniform(0.35, 0.65))
        win_rate = int((wins / total_games) * 100) if total_games > 0 else 0

        # Peak rank episode and act
        peak_ep = random.choice([7, 8, 9])  # Episodes 7, 8, or 9
        peak_act = random.randint(1, 3)

        return {
            "rank": rank_tier,
            "rr": rr,
            "leaderboard": leaderboard,
            "peakrank": peak_rank,
            "wr": win_rate,
            "numberofgames": total_games,
            "peakrankact": peak_act,
            "peakrankep": peak_ep,
            "statusgood": True,
            "statuscode": 200
        }

    def generate_player_stats(self) -> Dict[str, Any]:
        """Generate player performance stats (K/D, HS%)."""
        kills = random.randint(8, 35)
        deaths = random.randint(8, 30)
        kd = round(kills / max(deaths, 1), 2)

        # Headshot percentage (weighted towards 20-40% range)
        hs = int(random.gauss(30, 12))
        hs = max(5, min(80, hs))  # Clamp between 5-80%

        # Ranked rating earned/lost in last game
        rr_earned = random.randint(-30, 30)
        afk_penalty = random.choice([0, 0, 0, 0, 0, 3, 5, 8])  # Mostly 0, sometimes penalty

        return {
            "kd": kd,
            "hs": hs,
            "RankedRatingEarned": rr_earned,
            "AFKPenalty": afk_penalty
        }

    def generate_player_level(self) -> int:
        """Generate player account level."""
        # Weight towards 50-300 range
        level = int(random.gauss(150, 100))
        return max(20, min(500, level))

    # ==================== WEAPON SKINS ====================

    def generate_weapon_skin(self, weapon: str = "Vandal") -> str:
        """Generate weapon skin name.

        Args:
            weapon: Weapon name (e.g., "Vandal", "Phantom")

        Returns:
            Skin name string
        """
        skin_collections = {
            "Prime": ["Prime"],
            "Reaver": ["Reaver"],
            "Elderflame": ["Elderflame"],
            "Singularity": ["Singularity"],
            "Spectrum": ["Spectrum"],
            "Protocol 781-A": ["Protocol 781-A"],
            "Glitchpop": ["Glitchpop"],
            "Prelude to Chaos": ["Prelude to Chaos"],
            "Chronovoid": ["Chronovoid"],
            "Araxys": ["Araxys"],
            "Neptune": ["Neptune"],
            "Recon": ["Recon"],
            "Ion": ["Ion"],
            "Oni": ["Oni"],
            "Sentinels of Light": ["Sentinels of Light"],
            "Ruination": ["Ruination"],
            "Champions 2021": ["Champions 2021"],
            "Champions 2022": ["Champions 2022"],
            "Champions 2023": ["Champions 2023"],
            "Standard": ["Standard"],
        }

        collection = random.choice(list(skin_collections.keys()))

        # 30% chance of standard skin
        if random.random() < 0.3:
            return "Standard"

        return collection

    # ==================== MATCH DATA ====================

    def generate_match_id(self) -> str:
        """Generate realistic match ID."""
        return str(uuid.uuid4())

    def generate_player_identity(self, hide_level: bool = False, incognito: bool = False) -> Dict[str, Any]:
        """Generate player identity data.

        Args:
            hide_level: Whether account level is hidden
            incognito: Whether player is in streamer mode

        Returns:
            PlayerIdentity dict
        """
        return {
            "AccountLevel": self.generate_player_level(),
            "PlayerCardID": str(uuid.uuid4()),
            "PlayerTitleID": str(uuid.uuid4()),
            "HideAccountLevel": hide_level,
            "Incognito": incognito
        }

    def generate_agent_id(self) -> str:
        """Generate random agent UUID."""
        agents = [
            "5f8d3a7f-467b-97f3-062c-13acf203c006",  # Breach
            "f94c3b30-42be-e959-889c-5aa313dba261",  # Brimstone
            "22697a3d-8bee-8a1c-4daa-29eab488c492",  # Chamber
            "117ed9e3-49f3-6512-3ccf-0cada7e3823b",  # Cypher
            "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235",  # Deadlock
            "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc",  # Reyna
            "add6443a-41bd-e414-f6ad-e58d267f4e95",  # Jett
            "1e58de9c-4950-5125-93e9-a0aee9f98746",  # Killjoy
            "95b78ed7-4637-86d9-7e41-71ba8c293152",  # Harbor
            "bb2a4828-46eb-8cd1-e765-15848195d751",  # Neon
            "8e253930-4c05-31dd-1b6c-968525494517",  # Omen
            "eb93336a-449b-9c1b-0a54-a891f7921d69",  # Phoenix
            "f94c3b30-42be-e959-889c-5aa313dba261",  # Raze
            "569fdd95-4d10-43ab-ca70-79becc718b46",  # Sage
            "6f2a04ca-43e0-be17-7f36-b3908627744d",  # Skye
            "320b2a48-4d9b-a075-30f1-1f93a9b638fa",  # Sova
            "707eab51-4836-f488-046a-cda6bf494859",  # Viper
            "601dbbe7-43ce-be57-2a40-4abd24953621",  # Kay/o
        ]
        return random.choice(agents)

    def generate_coregame_player(self, team: str = "Blue", is_self: bool = False) -> Dict[str, Any]:
        """Generate a player for coregame (in-match).

        Args:
            team: "Blue" or "Red"
            is_self: Whether this is the current player

        Returns:
            Player dict matching coregame API structure
        """
        player_name = self.generate_player_name()
        puuid = self.current_puuid if is_self else player_name["Subject"]

        # 10% chance of streamer mode
        incognito = random.random() < 0.1

        return {
            "Subject": puuid,
            "TeamID": team,
            "CharacterID": self.generate_agent_id(),
            "PlayerIdentity": self.generate_player_identity(
                hide_level=random.random() < 0.05,
                incognito=incognito
            ),
            "SeasonalBadgeInfo": {},
            "IsCoach": False,
            "IsAssociated": True
        }

    def generate_coregame_stats(self, map_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate full coregame stats (active match).

        Args:
            map_id: Specific map ID, or None for random

        Returns:
            Coregame stats dict
        """
        maps = [
            "/Game/Maps/Ascent/Ascent",
            "/Game/Maps/Bind/Bind",
            "/Game/Maps/Haven/Triad",
            "/Game/Maps/Split/Bonsai",
            "/Game/Maps/Icebox/Port",
            "/Game/Maps/Breeze/Foxtrot",
            "/Game/Maps/Fracture/Canyon",
            "/Game/Maps/Pearl/Pitt",
            "/Game/Maps/Lotus/Jam",
            "/Game/Maps/Sunset/Juliett",
            "/Game/Maps/Abyss/Tango"
        ]

        if map_id is None:
            map_id = random.choice(maps)

        # Generate 10 players (5 per team)
        players = []

        # Add self player first (always on Blue team)
        players.append(self.generate_coregame_player(team="Blue", is_self=True))

        # Add 4 more Blue team players
        for _ in range(4):
            players.append(self.generate_coregame_player(team="Blue", is_self=False))

        # Add 5 Red team players
        for _ in range(5):
            players.append(self.generate_coregame_player(team="Red", is_self=False))

        # Shuffle to randomize order (but keep data consistent)
        random.shuffle(players)

        # Cache player data for consistent queries
        for player in players:
            if player["Subject"] not in self.player_cache:
                self.player_cache[player["Subject"]] = {
                    "rank": self.generate_rank_data(),
                    "stats": self.generate_player_stats(),
                    "agent": player["CharacterID"]
                }

        match_id = self.generate_match_id()

        return {
            "MatchID": match_id,
            "Version": random.randint(1, 100),
            "State": "IN_PROGRESS",
            "MapID": map_id,
            "ModeID": "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C",
            "ProvisioningFlow": "Matchmaking",
            "GamePodID": f"aresriot.aws-rclusterprod-use1-1.na-gp-ashburn-{random.randint(1,5)}.{random.randint(1000,9999)}",
            "AllMUCName": f"ares-coregame@ares-coregame-{match_id}.na1.pvp.net",
            "TeamMUCName": f"ares-coregame-blue@ares-coregame-{match_id}.na1.pvp.net",
            "TeamVoiceID": str(uuid.uuid4()),
            "IsReconnectable": True,
            "ConnectionDetails": {},
            "PostGameDetails": None,
            "Players": players,
            "MatchmakingData": None
        }

    def generate_pregame_stats(self) -> Dict[str, Any]:
        """Generate pregame stats (agent select)."""
        # Generate 5 players for ally team
        players = []

        # Add self first
        self_player = self.generate_coregame_player(team="Blue", is_self=True)
        self_player["CharacterSelectionState"] = "locked"
        self_player["PregamePlayerState"] = "locked_in"
        players.append(self_player)

        # Add 4 teammates
        for i in range(4):
            player = self.generate_coregame_player(team="Blue", is_self=False)
            # Random selection state
            player["CharacterSelectionState"] = random.choice(["locked", "selected", ""])
            player["PregamePlayerState"] = random.choice(["locked_in", "selecting", ""])
            players.append(player)

        # Cache player data
        for player in players:
            if player["Subject"] not in self.player_cache:
                self.player_cache[player["Subject"]] = {
                    "rank": self.generate_rank_data(),
                    "stats": self.generate_player_stats(),
                    "agent": player["CharacterID"]
                }

        match_id = self.generate_match_id()

        maps = [
            "/Game/Maps/Ascent/Ascent",
            "/Game/Maps/Bind/Bind",
            "/Game/Maps/Haven/Triad",
            "/Game/Maps/Split/Bonsai",
            "/Game/Maps/Icebox/Port",
        ]

        return {
            "ID": match_id,
            "Version": random.randint(1, 100),
            "Teams": [
                {
                    "TeamID": "Blue",
                    "Players": []
                }
            ],
            "AllyTeam": {
                "TeamID": "Blue",
                "Players": players
            },
            "EnemyTeam": None,
            "ObserverSubjects": [],
            "MatchCoaches": [],
            "EnemyTeamSize": 5,
            "EnemyTeamLockCount": 0,
            "PregameState": "character_select_active",
            "LastUpdated": int(time.time() * 1000),
            "MapID": random.choice(maps),
            "GamePodID": f"aresriot.aws-rclusterprod-use1-1.na-gp-ashburn-{random.randint(1,5)}.{random.randint(1000,9999)}",
            "Mode": "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C",
            "VoiceSessionID": str(uuid.uuid4()),
            "MUCName": f"ares-pregame@ares-pregame-{match_id}.na1.pvp.net",
            "QueueID": "competitive",
            "ProvisioningFlow": "Matchmaking",
            "IsRanked": True,
            "PhaseTimeRemainingNS": random.randint(10000000000, 80000000000),
            "altModesFlagADA": False
        }

    # ==================== PRESENCE DATA ====================

    def generate_presence_data(self, game_state: str = "INGAME") -> List[Dict[str, Any]]:
        """Generate presence data.

        Args:
            game_state: "INGAME", "PREGAME", or "MENUS"

        Returns:
            List of presence dicts
        """
        import base64

        # Generate private presence data (both nested and flat for compatibility)
        if game_state == "INGAME":
            private_data = {
                "isValid": True,
                "sessionLoopState": "INGAME",
                "partyOwnerMatchScoreAllyTeam": random.randint(0, 12),
                "partyOwnerMatchScoreEnemyTeam": random.randint(0, 12),
                "partyOwnerMatchCurrentTeam": "Blue",
                "partyOwnerProvisioningFlow": "Matchmaking",
                "provisioningFlow": "Matchmaking",
                "matchMap": "/Game/Maps/Ascent/Ascent",
                "partyId": str(uuid.uuid4()),
                "isPartyOwner": True,
                "partyState": "MATCHMAKING",
                "partyAccessibility": "CLOSED",
                "maxPartySize": 5,
                "queueId": "competitive",
                "partySize": random.randint(1, 5),
                "accountLevel": self.generate_player_level()
            }
        elif game_state == "PREGAME":
            private_data = {
                "isValid": True,
                "sessionLoopState": "PREGAME",
                "partyOwnerMatchMap": "/Game/Maps/Bind/Bind",
                "partyOwnerMatchCurrentTeam": "Blue",
                "partyOwnerProvisioningFlow": "Matchmaking",
                "provisioningFlow": "Matchmaking",
                "matchMap": "/Game/Maps/Bind/Bind",
                "partyId": str(uuid.uuid4()),
                "isPartyOwner": True,
                "partyState": "MATCHMAKING",
                "partyAccessibility": "OPEN",
                "maxPartySize": 5,
                "queueId": "competitive",
                "partySize": random.randint(1, 5),
                "accountLevel": self.generate_player_level()
            }
        else:  # MENUS
            queue_ids = ["competitive", "unrated", "spikerush", "deathmatch", "swiftplay"]
            private_data = {
                "isValid": True,
                "sessionLoopState": "MENUS",
                "partyOwnerSessionLoopState": "MENUS",
                "partyId": str(uuid.uuid4()),
                "isPartyOwner": True,
                "partyState": "DEFAULT",
                "partyAccessibility": random.choice(["OPEN", "CLOSED"]),
                "maxPartySize": 5,
                "queueId": random.choice(queue_ids),
                "partySize": random.randint(1, 3),
                "accountLevel": self.generate_player_level(),
                "isIdle": False
            }

        # Encode private data
        private_encoded = base64.b64encode(json.dumps(private_data).encode()).decode()

        return [
            {
                "puuid": self.current_puuid,
                "game_name": "MockPlayer",
                "game_tag": "NA01",
                "resource": "",
                "platform": "riot",
                "cid": "",
                "name": "",
                "pid": "",
                "private": private_encoded,
                "product": "valorant",
                "region": "na",
                "state": "dnd"
            }
        ]

    # ==================== RANK/MMR DATA ====================

    def generate_mmr_response(self, puuid: Optional[str] = None) -> Dict[str, Any]:
        """Generate MMR/rank API response.

        Args:
            puuid: Player PUUID (uses cached data if available)

        Returns:
            MMR response dict
        """
        if puuid and puuid in self.player_cache:
            cached_rank = self.player_cache[puuid]["rank"]
            rank_tier = cached_rank["rank"]
        else:
            rank_tier = None

        rank_data = self.generate_rank_data(rank_tier)

        # Current season ID
        season_id = "67e373c7-48f7-b422-641b-079ace30b427"

        # Previous season ID
        prev_season_id = "52e9749a-429b-7060-99fe-4595426a0cf7"

        seasonal_info = {
            season_id: {
                "SeasonID": season_id,
                "NumberOfWins": int(rank_data["numberofgames"] * rank_data["wr"] / 100),
                "NumberOfWinsWithPlacements": int(rank_data["numberofgames"] * rank_data["wr"] / 100),
                "NumberOfGames": rank_data["numberofgames"],
                "Rank": 0,
                "CapstoneWins": 0,
                "LeaderboardRank": rank_data["leaderboard"],
                "CompetitiveTier": rank_data["rank"],
                "RankedRating": rank_data["rr"],
                "WinsByTier": self._generate_wins_by_tier(rank_data["rank"]),
                "GamesNeededForRating": 0,
                "TotalWinsNeededForRank": 0
            },
            prev_season_id: {
                "SeasonID": prev_season_id,
                "NumberOfWins": random.randint(10, 100),
                "NumberOfWinsWithPlacements": random.randint(10, 100),
                "NumberOfGames": random.randint(20, 200),
                "Rank": 0,
                "CapstoneWins": 0,
                "LeaderboardRank": 0,
                "CompetitiveTier": random.randint(3, rank_data["rank"]),
                "RankedRating": random.randint(10, 90),
                "WinsByTier": None,
                "GamesNeededForRating": 0,
                "TotalWinsNeededForRank": 0
            }
        }

        return {
            "Version": random.randint(1, 1000),
            "Subject": puuid or self.current_puuid,
            "NewPlayerExperienceFinished": True,
            "QueueSkills": {
                "competitive": {
                    "TotalGamesNeededForRating": 0,
                    "TotalGamesNeededForLeaderboard": 0,
                    "CurrentSeasonGamesNeededForRating": 0,
                    "SeasonalInfoBySeasonID": seasonal_info
                }
            },
            "LatestCompetitiveUpdate": {
                "MatchID": self.generate_match_id(),
                "MapID": "/Game/Maps/Ascent/Ascent",
                "SeasonID": season_id,
                "MatchStartTime": int(time.time() * 1000) - random.randint(600000, 7200000),
                "TierAfterUpdate": rank_data["rank"],
                "TierBeforeUpdate": rank_data["rank"],
                "RankedRatingAfterUpdate": rank_data["rr"],
                "RankedRatingBeforeUpdate": max(0, rank_data["rr"] - rank_data.get("RankedRatingEarned", 0)),
                "RankedRatingEarned": rank_data.get("RankedRatingEarned", random.randint(-25, 25)),
                "RankedRatingPerformanceBonus": random.randint(0, 5),
                "CompetitiveMovement": "MOVEMENT_UNKNOWN",
                "AFKPenalty": 0
            },
            "IsLeaderboardAnonymized": False,
            "IsActRankBadgeHidden": False
        }

    def _generate_wins_by_tier(self, current_tier: int) -> Dict[str, int]:
        """Generate historical wins by tier."""
        wins_by_tier = {}

        # Add wins for tiers up to current tier
        for tier in range(3, min(current_tier + 1, 28)):
            wins = random.randint(0, 50)
            if wins > 0:
                wins_by_tier[str(tier)] = wins

        return wins_by_tier if wins_by_tier else None

    # ==================== LOADOUT DATA ====================

    def generate_loadout_data(self, match_id: str, players: List[Dict]) -> Dict[str, Any]:
        """Generate loadout data (weapon skins).

        Args:
            match_id: Match ID
            players: List of player dicts

        Returns:
            Loadouts dict
        """
        loadouts = []

        for player in players:
            weapons = {}

            # Generate loadout for common weapons
            weapon_uuids = [
                "9c82e19d-4575-0200-1a81-3eacf00cf872",  # Vandal
                "ee8e8d15-496b-07ac-e5f6-8fae5d4c7b1a",  # Phantom
                "e336c6b8-418d-9340-d77f-7a9e4cfe0702",  # Operator
                "29a0cfab-485b-f5d5-779a-b59f85e204a8",  # Classic
                "462080d1-4035-2937-7c09-27aa2a5c27a7",  # Spectre
                "910be174-449b-c412-ab22-d0873436b21b",  # Sheriff
                "2f59173c-4bed-b6c3-2191-dea9b58be9c7",  # Melee
            ]

            for weapon_uuid in weapon_uuids:
                weapons[weapon_uuid] = {
                    "Sockets": {
                        "bcef87d6-209b-46c6-8b19-fbe40bd95abc": {  # Skin socket
                            "Item": {
                                "ID": str(uuid.uuid4()),
                                "TypeID": "e7c63390-eda7-46e0-bb7a-a6abdacd2433"
                            }
                        },
                        "3ad1b2b2-acdb-4524-852f-954a76ddae0a": {  # Chroma socket
                            "Item": {
                                "ID": str(uuid.uuid4()),
                                "TypeID": "3ad1b2b2-acdb-4524-852f-954a76ddae0a"
                            }
                        },
                        "77258665-71d1-4623-bc72-44db9bd5b3b3": {  # Buddy socket
                            "Item": {
                                "ID": str(uuid.uuid4()) if random.random() < 0.5 else "",
                                "TypeID": "dd3bf334-87f3-40bd-b043-682a57a8dc3a"
                            }
                        }
                    }
                }

            loadouts.append({
                "Subject": player["Subject"],
                "Loadout": {
                    "Sprays": {},
                    "Items": weapons,
                    "Expressions": {
                        "AESSelections": []
                    }
                }
            })

        return {
            "Loadouts": loadouts,
            "LoadoutsValid": True
        }

    # ==================== NAME SERVICE ====================

    def generate_name_response(self, puuids: List[str]) -> List[Dict[str, str]]:
        """Generate name service response.

        Args:
            puuids: List of player PUUIDs

        Returns:
            List of name dicts
        """
        names = []

        for puuid in puuids:
            if puuid == self.current_puuid:
                names.append({
                    "Subject": puuid,
                    "GameName": "MockPlayer",
                    "TagLine": "NA01"
                })
            else:
                player_name = self.generate_player_name()
                names.append({
                    "Subject": puuid,
                    "GameName": player_name["GameName"],
                    "TagLine": player_name["TagLine"]
                })

        return names

    # ==================== COMPETITIVE UPDATES ====================

    def generate_competitive_updates(self, puuid: str) -> Dict[str, Any]:
        """Generate competitive updates response (recent match stats)."""
        matches = []

        # Generate 1 recent match
        match = {
            "MatchID": self.generate_match_id(),
            "MapID": "/Game/Maps/Ascent/Ascent",
            "SeasonID": "67e373c7-48f7-b422-641b-079ace30b427",
            "MatchStartTime": int(time.time() * 1000) - random.randint(600000, 3600000),
            "TierAfterUpdate": random.randint(3, 27),
            "TierBeforeUpdate": random.randint(3, 27),
            "RankedRatingAfterUpdate": random.randint(10, 100),
            "RankedRatingBeforeUpdate": random.randint(10, 100),
            "RankedRatingEarned": random.randint(-30, 30),
            "RankedRatingPerformanceBonus": random.randint(0, 5),
            "CompetitiveMovement": "MOVEMENT_UNKNOWN",
            "AFKPenalty": random.choice([0, 0, 0, 0, 3, 8])
        }

        matches.append(match)

        return {
            "Version": random.randint(1, 1000),
            "Subject": puuid,
            "Matches": matches
        }

    # ==================== MATCH DETAILS ====================

    def generate_match_details(self, match_id: str, puuid: str) -> Dict[str, Any]:
        """Generate detailed match data (for stats calculation)."""
        # Generate player stats for the specified puuid
        kills = random.randint(5, 35)
        deaths = random.randint(5, 30)
        assists = random.randint(0, 15)

        # Generate round-by-round damage stats
        num_rounds = random.randint(13, 26)  # 13-0 to 13-13
        round_results = []

        total_headshots = 0
        total_bodyshots = 0
        total_legshots = 0

        for _ in range(num_rounds):
            headshots = random.randint(0, 5)
            bodyshots = random.randint(0, 10)
            legshots = random.randint(0, 3)

            total_headshots += headshots
            total_bodyshots += bodyshots
            total_legshots += legshots

            round_results.append({
                "roundNum": _,
                "roundResult": random.choice(["Eliminated", "Bomb detonated", "Bomb defused"]),
                "roundCeremony": random.choice(["CeremonyDefault", "CeremonyFlawless", "CeremonyClutch"]),
                "playerStats": [
                    {
                        "subject": puuid,
                        "kills": [{"victim": str(uuid.uuid4())} for _ in range(random.randint(0, 3))],
                        "damage": [
                            {
                                "receiver": str(uuid.uuid4()),
                                "headshots": headshots,
                                "bodyshots": bodyshots,
                                "legshots": legshots
                            }
                        ],
                        "score": random.randint(50, 500)
                    }
                ]
            })

        return {
            "matchInfo": {
                "matchId": match_id,
                "mapId": "/Game/Maps/Ascent/Ascent",
                "gameMode": "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C",
                "isRanked": True,
                "queueID": "competitive"
            },
            "players": [
                {
                    "subject": puuid,
                    "gameName": "MockPlayer",
                    "tagLine": "NA01",
                    "teamId": "Blue",
                    "partyId": str(uuid.uuid4()),
                    "characterId": self.generate_agent_id(),
                    "stats": {
                        "kills": kills,
                        "deaths": deaths,
                        "assists": assists,
                        "score": kills * 200 + assists * 50
                    }
                }
            ],
            "teams": [
                {
                    "teamId": "Blue",
                    "won": random.choice([True, False]),
                    "roundsPlayed": num_rounds,
                    "roundsWon": random.randint(0, 13)
                },
                {
                    "teamId": "Red",
                    "won": random.choice([True, False]),
                    "roundsPlayed": num_rounds,
                    "roundsWon": random.randint(0, 13)
                }
            ],
            "roundResults": round_results
        }


# ==================== SINGLETON INSTANCE ====================

_mock_generator = None

def get_mock_generator() -> MockDataGenerator:
    """Get or create the singleton mock data generator."""
    global _mock_generator
    if _mock_generator is None:
        _mock_generator = MockDataGenerator()
    return _mock_generator


# ==================== CONVENIENCE FUNCTIONS ====================

def get_current_puuid() -> str:
    """Get the mock current player PUUID."""
    return get_mock_generator().current_puuid


def generate_mock_response(endpoint: str, method: str, **kwargs) -> Any:
    """Generate mock response for a given API endpoint.

    Args:
        endpoint: API endpoint path
        method: HTTP method
        **kwargs: Additional parameters (puuid, match_id, etc.)

    Returns:
        Mock response data matching VALORANT API structure
    """
    generator = get_mock_generator()

    # Parse endpoint to determine what data to return
    if "/entitlements/v1/token" in endpoint:
        # Entitlements token
        return {
            "accessToken": "mock_access_token_" + str(uuid.uuid4()),
            "subject": generator.current_puuid,
            "token": "mock_entitlement_token_" + str(uuid.uuid4())
        }

    elif "/chat/v4/presences" in endpoint:
        # Presences
        game_state = kwargs.get("game_state", "MENUS")
        return {
            "presences": generator.generate_presence_data(game_state)
        }

    elif "/core-game/v1/players/" in endpoint:
        # Current coregame match ID
        match_id = generator.generate_match_id()
        return {
            "Subject": generator.current_puuid,
            "MatchID": match_id,
            "Version": random.randint(1, 100)
        }

    elif "/core-game/v1/matches/" in endpoint and "/loadouts" in endpoint:
        # Loadouts
        match_id = kwargs.get("match_id", generator.generate_match_id())
        players = kwargs.get("players", [])
        return generator.generate_loadout_data(match_id, players)

    elif "/core-game/v1/matches/" in endpoint:
        # Coregame stats
        return generator.generate_coregame_stats()

    elif "/pregame/v1/players/" in endpoint:
        # Pregame match ID
        match_id = generator.generate_match_id()
        return {
            "Subject": generator.current_puuid,
            "MatchID": match_id,
            "Version": random.randint(1, 100)
        }

    elif "/pregame/v1/matches/" in endpoint:
        # Pregame stats
        return generator.generate_pregame_stats()

    elif "/mmr/v1/players/" in endpoint and "/competitiveupdates" in endpoint:
        # Competitive updates
        puuid = kwargs.get("puuid", generator.current_puuid)
        return generator.generate_competitive_updates(puuid)

    elif "/mmr/v1/players/" in endpoint:
        # MMR/Rank data
        puuid = kwargs.get("puuid", generator.current_puuid)
        return generator.generate_mmr_response(puuid)

    elif "/name-service/v2/players" in endpoint:
        # Name service
        puuids = kwargs.get("puuids", [generator.current_puuid])
        return generator.generate_name_response(puuids)

    elif "/match-details/v1/matches/" in endpoint:
        # Match details
        match_id = kwargs.get("match_id", generator.generate_match_id())
        puuid = kwargs.get("puuid", generator.current_puuid)
        return generator.generate_match_details(match_id, puuid)

    # Default: return empty success response
    return {"status": "ok"}


if __name__ == "__main__":
    # Test the mock data generator
    print("=== Testing Mock Data Generator ===\n")

    gen = MockDataGenerator(seed=42)

    print("1. Player Name:")
    print(json.dumps(gen.generate_player_name(), indent=2))

    print("\n2. Rank Data:")
    print(json.dumps(gen.generate_rank_data(), indent=2))

    print("\n3. Player Stats:")
    print(json.dumps(gen.generate_player_stats(), indent=2))

    print("\n4. Coregame Stats (5 players shown):")
    coregame = gen.generate_coregame_stats()
    print(f"Match ID: {coregame['MatchID']}")
    print(f"Map: {coregame['MapID']}")
    print(f"Players: {len(coregame['Players'])}")
    for i, player in enumerate(coregame['Players'][:5]):
        print(f"  Player {i+1}: Team={player['TeamID']}, Level={player['PlayerIdentity']['AccountLevel']}")

    print("\n5. MMR Response:")
    mmr = gen.generate_mmr_response()
    season_data = list(mmr['QueueSkills']['competitive']['SeasonalInfoBySeasonID'].values())[0]
    print(f"Rank Tier: {season_data['CompetitiveTier']}")
    print(f"RR: {season_data['RankedRating']}")
    print(f"Games: {season_data['NumberOfGames']}")

    print("\n=== Mock Data Generator Test Complete ===")
