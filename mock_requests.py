"""
Mock Request Interceptor for VALORANT Rank Yoinker (macOS Testing)

This module intercepts API calls from requestsV.py and returns mock data instead of
making real HTTP requests. It's designed to work as a drop-in replacement for the
Requests class when mock mode is enabled.

Usage:
    1. Enable mock mode in config.json: "mock_mode": true
    2. The application will automatically use this instead of real requests

Custom for macOS development - minimal changes to core application.
"""

import json
import time
import base64
from typing import Dict, Any, Optional
from mock_data import get_mock_generator, generate_mock_response, get_current_puuid


class MockResponse:
    """Mock HTTP response object that mimics requests.Response."""

    def __init__(self, json_data: Any, status_code: int = 200):
        self._json_data = json_data
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self.text = json.dumps(json_data) if isinstance(json_data, (dict, list)) else str(json_data)

    def json(self):
        """Return JSON data."""
        return self._json_data


class MockRequests:
    """Mock version of the Requests class that returns simulated data.

    This class matches the interface of src/requestsV.py::Requests but returns
    mock data instead of making real API calls.
    """

    def __init__(self, version, log, Error, game_state: str = "MENUS"):
        """Initialize mock requests.

        Args:
            version: Application version
            log: Logging function
            Error: Error handler class
            game_state: Initial game state (MENUS, PREGAME, or INGAME)
        """
        self.version = version
        self.log = log
        self.Error = Error
        self.headers = {}
        self.game_state = game_state

        # Mock lockfile
        self.lockfile = {
            'name': 'mock_lockfile',
            'PID': '12345',
            'port': '55555',
            'password': 'mock_password',
            'protocol': 'https'
        }

        # Mock region and URLs
        self.region = "na"
        self.pd_url = f"https://pd.na.a.pvp.net"
        self.glz_url = f"https://glz-na-1.na.a.pvp.net"

        # Get mock PUUID
        self.puuid = get_current_puuid()

        self.log("=" * 50)
        self.log("MOCK MODE ENABLED - Using simulated data")
        self.log("No connection to VALORANT required")
        self.log("=" * 50)

    @staticmethod
    def check_version(version, copy_run_update_script):
        """Mock version check - always reports up to date."""
        print(f"[MOCK] Version check: {version} (mock mode - skipping update check)")

    @staticmethod
    def check_status():
        """Mock status check - always reports good status."""
        print("[MOCK] Status check: OK (mock mode)")

    def fetch(self, url_type: str, endpoint: str, method: str, rate_limit_seconds=5) -> Any:
        """Mock API fetch that returns simulated data.

        Args:
            url_type: "glz", "pd", "local", or "custom"
            endpoint: API endpoint path
            method: HTTP method
            rate_limit_seconds: Rate limit delay (ignored in mock)

        Returns:
            MockResponse or dict with mock data
        """
        # Add small delay to simulate network latency
        time.sleep(0.05)

        self.log(f"[MOCK] fetch: url_type='{url_type}', endpoint='{endpoint}', method='{method}'")

        try:
            # Determine what data to return based on endpoint
            if url_type == "local":
                # Local client API endpoints
                if "/entitlements/v1/token" in endpoint:
                    return generate_mock_response(endpoint, method)

                elif "/chat/v4/presences" in endpoint:
                    return generate_mock_response(endpoint, method, game_state=self.game_state)

                elif "/chat/v6/messages" in endpoint:
                    # Chat messages - return empty for now
                    return {"messages": []}

            elif url_type == "glz":
                # GLZ API endpoints (game state, matches)
                if f"/core-game/v1/players/{self.puuid}" in endpoint:
                    return generate_mock_response(endpoint, method)

                elif "/core-game/v1/matches/" in endpoint and "/loadouts" in endpoint:
                    # Extract match_id from endpoint
                    match_id = endpoint.split("/matches/")[1].split("/")[0]
                    # Get current coregame stats to get players
                    coregame = get_mock_generator().generate_coregame_stats()
                    return generate_mock_response(endpoint, method, match_id=match_id, players=coregame["Players"])

                elif "/core-game/v1/matches/" in endpoint:
                    return generate_mock_response(endpoint, method)

                elif f"/pregame/v1/players/{self.puuid}" in endpoint:
                    return generate_mock_response(endpoint, method)

                elif "/pregame/v1/matches/" in endpoint:
                    return generate_mock_response(endpoint, method)

            elif url_type == "pd":
                # PD API endpoints (ranks, stats, names)
                if "/mmr/v1/players/" in endpoint and "/competitiveupdates" in endpoint:
                    # Extract puuid from endpoint
                    puuid = endpoint.split("/players/")[1].split("/")[0]
                    response_data = generate_mock_response(endpoint, method, puuid=puuid)
                    return MockResponse(response_data)

                elif "/mmr/v1/players/" in endpoint:
                    # Extract puuid from endpoint
                    puuid = endpoint.split("/players/")[1]
                    response_data = generate_mock_response(endpoint, method, puuid=puuid)
                    return MockResponse(response_data)

                elif "/name-service/v2/players" in endpoint:
                    # Names endpoint - this is a PUT request with body
                    # For mock, we'll generate names for some mock PUUIDs
                    num_players = 5  # Default number of players
                    mock_puuids = [get_current_puuid()] + [str(i) for i in range(num_players - 1)]
                    response_data = generate_mock_response(endpoint, method, puuids=mock_puuids)
                    return MockResponse(response_data)

                elif "/match-details/v1/matches/" in endpoint:
                    # Extract match_id
                    match_id = endpoint.split("/matches/")[1]
                    puuid = self.puuid
                    response_data = generate_mock_response(endpoint, method, match_id=match_id, puuid=puuid)
                    return MockResponse(response_data, status_code=200)

            elif url_type == "custom":
                # Custom external API calls
                if "valorant-api.com" in endpoint:
                    # Return empty success for now (external API)
                    return {"data": [], "status": 200}

                elif "content-service" in endpoint:
                    # Content service (seasons, etc.)
                    return self._generate_content_service_response()

            # Default: return mock success
            self.log(f"[MOCK] No specific handler for endpoint: {endpoint}")
            return generate_mock_response(endpoint, method)

        except Exception as e:
            self.log(f"[MOCK] Error generating mock response: {e}")
            import traceback
            self.log(traceback.format_exc())
            return MockResponse({"error": str(e)}, status_code=500)

    def _generate_content_service_response(self) -> Dict[str, Any]:
        """Generate mock content service response (seasons, acts, etc.)."""
        import uuid

        return {
            "DisabledIDs": [],
            "Seasons": [
                {
                    "ID": "67e373c7-48f7-b422-641b-079ace30b427",
                    "Name": "EPISODE 9: ACT III",
                    "Type": "act",
                    "StartTime": "2024-10-22T17:00:00Z",
                    "EndTime": "2025-01-08T17:00:00Z",
                    "IsActive": True
                },
                {
                    "ID": "52e9749a-429b-7060-99fe-4595426a0cf7",
                    "Name": "EPISODE 9: ACT II",
                    "Type": "act",
                    "StartTime": "2024-08-28T17:00:00Z",
                    "EndTime": "2024-10-22T17:00:00Z",
                    "IsActive": False
                },
                {
                    "ID": str(uuid.uuid4()),
                    "Name": "EPISODE 9",
                    "Type": "episode",
                    "StartTime": "2024-06-26T17:00:00Z",
                    "EndTime": "2025-01-08T17:00:00Z",
                    "IsActive": True
                }
            ],
            "Events": []
        }

    def get_region(self):
        """Mock region detection."""
        self.log("[MOCK] get_region: returning 'na'")
        return ["na", ["na", "1"]]

    def get_current_version(self):
        """Mock version detection."""
        version = "release-09.09-shipping-8-2824111"
        self.log(f"[MOCK] get_current_version: {version}")
        return version

    def get_lockfile(self, ignoreLockfile=False):
        """Mock lockfile reading."""
        self.log("[MOCK] get_lockfile: returning mock lockfile")
        return self.lockfile

    def get_headers(self, refresh=False, init=False):
        """Mock headers generation."""
        if not self.headers or refresh:
            self.headers = {
                'Authorization': f"Bearer mock_access_token",
                'X-Riot-Entitlements-JWT': "mock_entitlement_token",
                'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                         "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                         "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
                'X-Riot-ClientVersion': self.get_current_version(),
                "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
            }
            self.log("[MOCK] get_headers: generated mock headers")

        return self.headers

    def set_game_state(self, state: str):
        """Set the mock game state.

        Args:
            state: "MENUS", "PREGAME", or "INGAME"
        """
        self.game_state = state
        self.log(f"[MOCK] Game state changed to: {state}")


def create_mock_requests(version, log, Error, game_state="MENUS"):
    """Factory function to create MockRequests instance.

    Args:
        version: Application version
        log: Logging function
        Error: Error handler
        game_state: Initial game state

    Returns:
        MockRequests instance
    """
    return MockRequests(version, log, Error, game_state)
