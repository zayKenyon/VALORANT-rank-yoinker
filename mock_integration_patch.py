"""
Mock Integration Patch for main.py

This file contains the minimal code changes needed to integrate mock mode into main.py.
Apply these changes to enable mock mode without modifying the core application logic.

INTEGRATION INSTRUCTIONS:
=========================

1. At the top of main.py, after the imports section (around line 40), add:

    # Mock mode support for macOS testing (custom addition)
    try:
        from src.config import Config as ConfigCheck
        temp_cfg = ConfigCheck(lambda x: None)  # Temporary config instance
        MOCK_MODE_ENABLED = temp_cfg.__dict__.get("mock_mode", False)
    except:
        MOCK_MODE_ENABLED = False

2. Replace the line that creates the Requests instance (around line 100):

    OLD:
        Requests = Requests(version, log, ErrorSRC)

    NEW:
        # Check for mock mode
        if MOCK_MODE_ENABLED:
            from mock_requests import create_mock_requests
            Requests = create_mock_requests(version, log, ErrorSRC, game_state="MENUS")
            print("\\n" + "=" * 60)
            print("MOCK MODE ACTIVE - Using simulated data")
            print("No VALORANT connection required (macOS testing)")
            print("=" * 60 + "\\n")
        else:
            Requests = Requests(version, log, ErrorSRC)

3. In src/constants.py, add to DEFAULT_CONFIG (around line 220):

    "mock_mode": False,  # Enable mock mode for macOS testing (custom addition)

That's it! These minimal changes enable mock mode while keeping the codebase
compatible with upstream updates.

ALTERNATIVE: No-Code Integration
================================

If you don't want to modify main.py at all, you can:

1. Run: python run_mock_test.py --setup-only
   (This enables mock_mode in config.json)

2. Set environment variable:
   export MOCK_MODE=1
   python main.py

3. The mock system will automatically intercept requests.

TESTING:
========

After integration:
1. Enable mock mode: Add "mock_mode": true to config.json
2. Run: python main.py
3. Application runs with mock data, no VALORANT required

Or use the test runner:
1. Run: python run_mock_test.py --state ingame
2. See simulated match data

REVERTING:
==========

To disable mock mode:
1. Set "mock_mode": false in config.json, OR
2. Remove the "mock_mode" key entirely

The application will work normally with real VALORANT data.
"""

# Example of minimal integration code
def integrate_mock_mode_example():
    """
    Example showing how mock mode integrates into main.py.
    This is for reference only - see instructions above for actual integration.
    """

    # Step 1: Check for mock mode at startup
    from src.config import Config
    cfg = Config(lambda x: None)
    mock_mode = cfg.__dict__.get("mock_mode", False)

    # Step 2: Create appropriate Requests instance
    if mock_mode:
        from mock_requests import create_mock_requests
        Requests = create_mock_requests(version="2.91", log=print, Error=None)
        print("[MOCK MODE] Using simulated data")
    else:
        from src.requestsV import Requests as RealRequests
        Requests = RealRequests(version="2.91", log=print, Error=None)
        print("[REAL MODE] Connecting to VALORANT")

    # Step 3: Use Requests normally - the rest of the code doesn't change!
    # The mock_requests.MockRequests class has the same interface as
    # src.requestsV.Requests, so all existing code works without modification.

    # Example API calls that work with both real and mock mode:
    lockfile = Requests.get_lockfile()
    headers = Requests.get_headers()
    presence = Requests.fetch("local", "/chat/v4/presences", "get")
    rank_data = Requests.fetch("pd", f"/mmr/v1/players/{Requests.puuid}", "get")

    return Requests


if __name__ == "__main__":
    print(__doc__)
