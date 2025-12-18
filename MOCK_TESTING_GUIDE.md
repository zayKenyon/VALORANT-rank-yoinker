# Mock Testing Guide for macOS Development

Complete guide to using the mock data system for testing VALORANT Rank Yoinker on macOS without VALORANT running.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Test Scenarios](#test-scenarios)
5. [Integration Methods](#integration-methods)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)
8. [Creating Custom Scenarios](#creating-custom-scenarios)

---

## Quick Start

### 5-Minute Setup

```bash
# 1. Install dependencies (if not already done)
pip install -r requirements.txt

# 2. Run the test runner
python run_mock_test.py --state ingame

# That's it! You should see a simulated match with 10 players.
```

### Enable Mock Mode in Application

```bash
# 1. Setup mock mode in config
python run_mock_test.py --setup-only

# 2. Run the application normally
python main.py

# The application will use mock data instead of connecting to VALORANT
```

---

## Installation

### Prerequisites

- Python 3.10 or 3.11
- macOS (or any OS where VALORANT isn't available)
- All dependencies from `requirements.txt`

### Install Mock System

The mock system is already included! No additional installation needed.

**Files included**:
- `mock_data.py` - Data generator
- `mock_requests.py` - Request interceptor
- `run_mock_test.py` - Test runner
- `mock_integration_patch.py` - Integration guide
- `MOCK_TESTING_GUIDE.md` - This file

---

## Basic Usage

### Method 1: Standalone Test Runner (Recommended for Testing)

Run simulated scenarios without modifying the main application:

```bash
# Test in-game state (default)
python run_mock_test.py

# Test pregame (agent select)
python run_mock_test.py --state pregame

# Test menu state
python run_mock_test.py --state menus

# Use specific random seed for reproducibility
python run_mock_test.py --seed 42

# Test different scenarios
python run_mock_test.py --scenario high_elo
python run_mock_test.py --scenario new_players
```

### Method 2: Full Application with Mock Data

Run the complete application using mock data:

```bash
# 1. Enable mock mode
python run_mock_test.py --setup-only

# 2. Run application
python main.py

# 3. To disable mock mode:
# Edit config.json and set "mock_mode": false
```

### Method 3: Environment Variable (No Config Changes)

```bash
# Set environment variable
export MOCK_MODE=1

# Run application
python main.py

# Unset when done
unset MOCK_MODE
```

---

## Test Scenarios

### Available Scenarios

#### 1. Mixed Ranks (Default)
Players from Iron to Radiant, most realistic distribution:

```bash
python run_mock_test.py --scenario mixed
```

**Features**:
- Players ranging from Iron 1 to Radiant
- Most players in Silver-Diamond range
- Some players with high headshot %
- Variety of account levels (20-500)
- Random party formations

#### 2. High ELO
All players Diamond 1 or higher:

```bash
python run_mock_test.py --scenario high_elo
```

**Features**:
- Diamond 1 minimum rank
- Several Immortal/Radiant players
- High account levels (200+)
- Better stats (higher HS%, K/D)
- More competitive match

#### 3. New Players
Mostly unranked and low rank players:

```bash
python run_mock_test.py --scenario new_players
```

**Features**:
- Mostly Iron-Silver ranks
- Several unranked players
- Lower account levels (20-100)
- More varied stats
- Testing for edge cases

#### 4. Random
Completely random generation each time:

```bash
python run_mock_test.py --scenario random
```

**Features**:
- No weighted distribution
- Pure randomness
- Good for stress testing
- Different results every run

### Game States

#### MENUS (Lobby)
Shows party information and lobby status:

```bash
python run_mock_test.py --state menus
```

**What's shown**:
- Party size
- Queue type (Competitive, Unrated, etc.)
- Account level
- Lobby status

#### PREGAME (Agent Select)
Shows team composition during agent selection:

```bash
python run_mock_test.py --state pregame
```

**What's shown**:
- 5 ally team players
- Agent selection status (locked, selected, not selected)
- Player ranks and levels
- Map information

#### INGAME (Active Match)
Full 10-player match display:

```bash
python run_mock_test.py --state ingame
```

**What's shown**:
- All 10 players (5 per team)
- Full rank information
- Performance stats (K/D, HS%, W/R)
- Peak ranks and RR
- Account levels
- Team colors (Blue/Red)

---

## Integration Methods

### Option A: Minimal Integration (Recommended)

Modify only 2 files with small additions:

#### Step 1: Add mock_mode flag to config

Edit `src/constants.py`, in the `DEFAULT_CONFIG` dict:

```python
"flags": {
    # ... existing flags ...
    "mock_mode": False,  # Add this line
}
```

#### Step 2: Add mock check to main.py

After imports (around line 40):

```python
# Mock mode support for macOS testing
try:
    from src.config import Config as ConfigCheck
    temp_cfg = ConfigCheck(lambda x: None)
    MOCK_MODE_ENABLED = temp_cfg.__dict__.get("mock_mode", False)
except:
    MOCK_MODE_ENABLED = False
```

At Requests initialization (around line 100):

```python
# Check for mock mode
if MOCK_MODE_ENABLED:
    from mock_requests import create_mock_requests
    Requests = create_mock_requests(version, log, ErrorSRC, game_state="MENUS")
    print("\n" + "=" * 60)
    print("MOCK MODE ACTIVE - Using simulated data")
    print("=" * 60 + "\n")
else:
    Requests = Requests(version, log, ErrorSRC)
```

#### Step 3: Enable and test

```bash
# Enable mock mode in config.json
{
    "mock_mode": true
}

# Run application
python main.py
```

### Option B: Zero-Modification Integration

Don't modify core files at all:

#### Step 1: Create launcher script

Create `run_mock.sh`:

```bash
#!/bin/bash
export MOCK_MODE=1
python main.py
```

#### Step 2: Make executable and run

```bash
chmod +x run_mock.sh
./run_mock.sh
```

### Option C: Test Runner Only

Don't integrate with main application, use standalone tester:

```bash
# Just use the test runner for development
python run_mock_test.py --state ingame

# No changes to main application needed!
```

---

## Troubleshooting

### Issue: "Module not found: mock_data"

**Solution**: Make sure you're in the project root directory:

```bash
cd /path/to/VALORANT-rank-yoinker
python run_mock_test.py
```

### Issue: "ImportError: cannot import name 'Config'"

**Solution**: Install all dependencies:

```bash
pip install -r requirements.txt
```

### Issue: Mock mode not activating

**Check**:

1. Is `mock_mode: true` in config.json?
   ```bash
   cat config.json | grep mock_mode
   ```

2. Did you add the integration code to main.py?
   ```bash
   grep "MOCK_MODE_ENABLED" main.py
   ```

3. Are mock files in the right place?
   ```bash
   ls mock_*.py
   # Should show: mock_data.py, mock_requests.py
   ```

### Issue: "AttributeError" when running mock mode

**Cause**: Mock responses might not match expected structure

**Solution**: Check which endpoint failed and update `mock_data.py`:

```python
# Find the failing endpoint in mock_data.py
# Update the generate_mock_response() function to return correct structure
```

### Issue: Application crashes in mock mode

**Debug**:

```bash
# Run with verbose logging
python main.py 2>&1 | tee debug.log

# Check logs directory
ls logs/
cat logs/log-*.txt | tail -100
```

**Common causes**:
- Missing mock response for a specific endpoint
- Incorrect data structure in mock response
- Platform-specific code running (Windows commands on macOS)

### Issue: Test runner shows "Unknown" for agents/ranks

**This is normal** - The test runner uses simplified display for demo purposes.

**To see real agent/rank names**:
- Integrate with full application (Method A or B above)
- The full application has all the agent and rank data

---

## Advanced Usage

### Custom Seed for Reproducible Tests

```bash
# Use same seed to get identical results
python run_mock_test.py --seed 42
python run_mock_test.py --seed 42  # Same output

# Different seed = different data
python run_mock_test.py --seed 123
python run_mock_test.py --seed 456
```

### Combining Options

```bash
# High ELO pregame with specific seed
python run_mock_test.py --state pregame --scenario high_elo --seed 100

# Multiple cycles (if supported)
python run_mock_test.py --cycles 3
```

### Testing Specific Edge Cases

Edit `mock_data.py` to create specific scenarios:

```python
# Force all players to be Radiant
def generate_rank_data(self, rank_tier: Optional[int] = None) -> Dict[str, Any]:
    return self.generate_rank_data(rank_tier=27)  # Force Radiant

# Force all players to be unranked
def generate_rank_data(self, rank_tier: Optional[int] = None) -> Dict[str, Any]:
    return self.generate_rank_data(rank_tier=0)  # Force unranked

# Force specific K/D
def generate_player_stats(self) -> Dict[str, Any]:
    return {"kd": 2.5, "hs": 45, ...}
```

### Testing API Error Scenarios

Modify `mock_requests.py` to simulate errors:

```python
def fetch(self, url_type: str, endpoint: str, method: str):
    # Simulate 404 error
    if "/specific-endpoint/" in endpoint:
        return MockResponse({"errorCode": "RESOURCE_NOT_FOUND"}, status_code=404)

    # Simulate rate limit
    if random.random() < 0.1:  # 10% chance
        return MockResponse({"errorCode": "RATE_LIMITED"}, status_code=429)
```

### Stress Testing

Generate matches with extreme values:

```bash
# Create custom scenario in mock_data.py
def generate_stress_test_match(self):
    """Generate match with extreme values."""
    return {
        # All Radiant players
        # 500+ account levels
        # Perfect 100% HS
        # 100 game winstreak
        ...
    }
```

---

## Creating Custom Scenarios

### Method 1: Edit mock_data.py

Add a new scenario to the generator:

```python
# In MockDataGenerator class

def generate_custom_scenario(self) -> Dict[str, Any]:
    """My custom test scenario."""

    # Example: All players same rank
    target_rank = 15  # Platinum 1

    players = []
    for i in range(10):
        player = self.generate_coregame_player(
            team="Blue" if i < 5 else "Red",
            is_self=(i == 0)
        )

        # Force specific rank
        self.player_cache[player["Subject"]] = {
            "rank": self.generate_rank_data(rank_tier=target_rank),
            "stats": self.generate_player_stats(),
            "agent": player["CharacterID"]
        }

        players.append(player)

    return {
        "MatchID": self.generate_match_id(),
        "Players": players,
        # ... rest of match data
    }
```

### Method 2: Create JSON Scenario File

Create `mock_data/my_scenario.json`:

```json
{
    "name": "My Custom Scenario",
    "description": "All players are Diamond with high stats",
    "players": [
        {
            "name": "Player1#NA01",
            "rank": 18,
            "rr": 75,
            "kd": 1.8,
            "hs": 40,
            "level": 250
        },
        // ... more players
    ]
}
```

Then load it in `mock_data.py`:

```python
def load_scenario_from_file(self, filename: str):
    """Load scenario from JSON file."""
    path = self.mock_dir / filename
    with open(path, 'r') as f:
        return json.load(f)
```

### Method 3: Runtime Customization

Pass parameters to test runner:

```bash
# Edit run_mock_test.py to accept custom parameters
python run_mock_test.py --min-rank 18 --max-rank 24 --avg-level 300
```

---

## Performance Tips

### Faster Testing

```bash
# Skip cycles (run once)
python run_mock_test.py --cycles 1

# Use fixed seed (consistent data)
python run_mock_test.py --seed 42

# Test only one state at a time
python run_mock_test.py --state ingame
```

### Memory Usage

Mock data is generated on-demand and cached. For large tests:

```python
# In mock_data.py, clear cache periodically
def clear_cache(self):
    """Clear player cache to free memory."""
    self.player_cache = {}
```

---

## Testing Checklist

Before submitting changes or testing features:

### Basic Tests
- [ ] Menu state works: `python run_mock_test.py --state menus`
- [ ] Pregame state works: `python run_mock_test.py --state pregame`
- [ ] In-game state works: `python run_mock_test.py --state ingame`

### Scenario Tests
- [ ] Mixed ranks: `python run_mock_test.py --scenario mixed`
- [ ] High ELO: `python run_mock_test.py --scenario high_elo`
- [ ] New players: `python run_mock_test.py --scenario new_players`

### Integration Tests
- [ ] Full app with mock mode: `python main.py` (with mock_mode: true)
- [ ] Config toggle works: Switch mock_mode on/off
- [ ] No errors in logs: Check `logs/log-*.txt`

### Edge Cases
- [ ] All Radiant players (edit mock_data.py)
- [ ] All unranked players
- [ ] Single player (Range mode)
- [ ] Mixed teams (some streamer mode)

---

## Example Workflows

### Workflow 1: Feature Development

```bash
# 1. Enable mock mode
python run_mock_test.py --setup-only

# 2. Develop feature
# ... edit code ...

# 3. Test with mock data
python main.py

# 4. Verify different states
python run_mock_test.py --state pregame
python run_mock_test.py --state ingame

# 5. Disable mock mode
# Edit config.json: "mock_mode": false

# 6. Test on real system (if available)
python main.py  # with VALORANT running
```

### Workflow 2: Bug Reproduction

```bash
# 1. Create specific scenario
# Edit mock_data.py to match bug conditions

# 2. Run with fixed seed
python run_mock_test.py --seed 42

# 3. Debug with that scenario
# ... fix bug ...

# 4. Verify fix with same seed
python run_mock_test.py --seed 42

# 5. Test with random seed
python run_mock_test.py
```

### Workflow 3: UI Testing

```bash
# 1. Test with many different scenarios
for seed in {1..10}; do
    echo "Testing with seed $seed"
    python run_mock_test.py --seed $seed --state ingame
    sleep 2
done

# 2. Test all states
for state in menus pregame ingame; do
    echo "Testing $state state"
    python run_mock_test.py --state $state
    sleep 2
done

# 3. Verify display looks good in all cases
```

---

## FAQ

**Q: Do I need VALORANT installed to use mock mode?**
A: No! That's the whole point. Mock mode simulates VALORANT data without the game.

**Q: Will mock mode work on Windows?**
A: Yes! Though it's designed for macOS, it works anywhere for testing without VALORANT.

**Q: Can I use mock mode with the real application?**
A: Yes, see [Integration Methods](#integration-methods) above.

**Q: How do I add a new API endpoint to the mock system?**
A: Edit `mock_data.py`, add a handler in `generate_mock_response()` function.

**Q: Can I contribute my custom scenarios?**
A: Absolutely! Create a PR with your JSON scenario files in `mock_data/`.

**Q: Does mock mode slow down the application?**
A: No, it's actually faster since no real network requests are made!

**Q: How realistic is the mock data?**
A: Very realistic - it matches actual VALORANT API structures and uses real rank distributions.

---

## Next Steps

1. **Try the quick start**: `python run_mock_test.py`
2. **Read MERGE_STRATEGY.md** for keeping mock system updated
3. **Check .aimrules** for detailed API documentation
4. **Create your own scenarios** for specific test cases

## Support

- **Issues**: Create a GitHub issue with `[MOCK]` tag
- **Questions**: See `.aimrules` for architecture details
- **Updates**: Check MERGE_STRATEGY.md when syncing upstream

---

**Happy Testing!** 🎮✨
