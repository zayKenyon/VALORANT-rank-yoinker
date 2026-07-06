import unittest
import sys
import os
import threading
import time
from unittest.mock import MagicMock, patch

# Ensure the root project directory is in the path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.content import hex_to_rgb, Content
from src.player_stats import PlayerStats
from src.requestsV import Requests


class TestVryImprovements(unittest.TestCase):

    def test_hex_to_rgb(self):
        # Test valid hex values
        self.assertEqual(hex_to_rgb("fd4556ff"), (253, 69, 86))
        self.assertEqual(hex_to_rgb("#fd4556"), (253, 69, 86))
        self.assertEqual(hex_to_rgb("000000"), (0, 0, 0))
        self.assertEqual(hex_to_rgb("ffffff"), (255, 255, 255))
        
        # Test invalid hex values
        self.assertIsNone(hex_to_rgb(""))
        self.assertIsNone(hex_to_rgb(None))
        self.assertIsNone(hex_to_rgb("invalid"))
        self.assertIsNone(hex_to_rgb("123"))

    def test_player_stats_cache_thread_safety(self):
        # Mock requests client and configuration
        mock_requests = MagicMock()
        mock_config = MagicMock()
        
        # We want to simulate slow HTTP fetch to verify that wait works and only 1 fetch happens
        fetch_call_count = 0
        fetch_lock = threading.Lock()
        
        def slow_fetch(url_type, endpoint, method):
            nonlocal fetch_call_count
            with fetch_lock:
                fetch_call_count += 1
            time.sleep(0.1)  # Simulate network latency
            
            # Return a mock response object
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_ok = True
            mock_resp.json.return_value = {"match_id": "test_match", "players": []}
            return mock_resp

        mock_requests.fetch.side_effect = slow_fetch
        
        player_stats = PlayerStats(mock_requests, log=MagicMock(), config=mock_config)
        
        # Let's start 10 threads trying to fetch the same match ID simultaneously
        match_id = "test-match-uuid-12345"
        threads = []
        results = [None] * 10
        
        def worker(index):
            results[index] = player_stats._get_match_details_cached(match_id)
            
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # Verify all threads successfully got the match details
        for res in results:
            self.assertIsNotNone(res)
            self.assertEqual(res["match_id"], "test_match")
            
        # Verify that only 1 HTTP request was made
        self.assertEqual(fetch_call_count, 1)

    @patch("requests.get")
    @patch("builtins.input", return_value="n")
    def test_requests_timeouts(self, mock_input, mock_get):
        # Setup mocks
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"tag_name": "3.00", "assets": []}]
        mock_get.return_value = mock_resp
        
        # Test check_version timeout passing
        try:
            Requests.check_version("2.00", MagicMock())
        except Exception:
            pass
            
        # Assert requests.get was called with timeout parameter
        args, kwargs = mock_get.call_args
        self.assertIn("timeout", kwargs)
        self.assertEqual(kwargs["timeout"], 3)


    def test_estimated_remaining_time(self):
        from src.player_stats import get_estimated_remaining_time
        # Competitive / Unrated score checks
        self.assertEqual(get_estimated_remaining_time("competitive", 12, 12), "~3 min")
        self.assertEqual(get_estimated_remaining_time("unrated", 0, 0), "~30 min")
        self.assertEqual(get_estimated_remaining_time("competitive", 13, 10), "0 min (Finished)")
        
        # Swiftplay checks
        self.assertEqual(get_estimated_remaining_time("swiftplay", 4, 4), "~3 min")
        self.assertEqual(get_estimated_remaining_time("swiftplay", 0, 0), "~10 min")
        
        # Invalid / Unhandled modes
        self.assertIsNone(get_estimated_remaining_time("deathmatch", 10, 5))
        self.assertIsNone(get_estimated_remaining_time("competitive", "invalid", 0))

    def test_agent_meta(self):
        from src.colors import Colors
        from src.constants import AGENT_META
        
        agent_dict = {"jett-uuid": "Jett", "sage-uuid": "Sage"}
        colors_inst = Colors(log=MagicMock(), hide_names=False, agent_dict=agent_dict, AGENTCOLORLIST={"jett": (255, 0, 0)})
        
        # Check display name logic with meta tags
        display_jett = colors_inst.get_agent_from_uuid("jett-uuid")
        self.assertIn("Jett", colors_inst.escape_ansi(display_jett))
        self.assertIn(AGENT_META["jett"], colors_inst.escape_ansi(display_jett))

    def test_fav_weapon_extraction(self):
        mock_requests = MagicMock()
        mock_config = MagicMock()
        
        # Construct mock match detail data with kills
        match_data = {
            "roundResults": [],
            "players": [
                {
                    "subject": "player-puuid",
                    "stats": {"kills": 3, "deaths": 2}
                }
            ],
            "kills": [
                {
                    "killer": "player-puuid",
                    "finishingDamage": {"damageItem": "vandal-uuid"}
                },
                {
                    "killer": "player-puuid",
                    "finishingDamage": {"damageWeapon": "vandal-uuid"}
                },
                {
                    "killer": "player-puuid",
                    "finishingDamage": {"damageItem": "phantom-uuid"}
                },
                {
                    "killer": "other-player",
                    "finishingDamage": {"damageItem": "phantom-uuid"}
                }
            ]
        }
        
        player_stats = PlayerStats(mock_requests, log=MagicMock(), config=mock_config)
        # Mock the weapon dict directly to bypass HTTP request in test
        player_stats.weapon_dict = {
            "vandal-uuid": "Vandal",
            "phantom-uuid": "Phantom"
        }
        
        result = player_stats._process_match_data(
            "player-puuid",
            match_data,
            match_summary={},
            win_rate_last_20=50,
            avg_rr_gain=20,
            streak=1,
            streak_type="win"
        )
        
        # Vandal has 2 kills from player-puuid, Phantom has 1 kill from player-puuid.
        # So favorite weapon should be Vandal with 2 kills.
        self.assertEqual(result["fav_weapon"], "Vandal")
        self.assertEqual(result["fav_weapon_kills"], 2)


if __name__ == "__main__":
    unittest.main()
