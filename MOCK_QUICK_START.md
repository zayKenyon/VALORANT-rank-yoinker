# Mock System Quick Start

**TL;DR**: Test VALORANT Rank Yoinker on macOS without VALORANT.

---

## ⚡ Instant Test (No Setup)

```bash
# See simulated 10-player match
python run_mock_test.py
```

That's it! You should see a formatted table with player stats.

---

## 📋 Quick Commands

### Test Different States

```bash
python run_mock_test.py --state ingame    # Active match (default)
python run_mock_test.py --state pregame   # Agent select
python run_mock_test.py --state menus     # Lobby
```

### Test Different Scenarios

```bash
python run_mock_test.py --scenario mixed      # Mixed ranks (default)
python run_mock_test.py --scenario high_elo   # All Diamond+
python run_mock_test.py --scenario new_players # Low ranks/unranked
```

### Use Specific Seed (Reproducible)

```bash
python run_mock_test.py --seed 42
python run_mock_test.py --seed 42  # Same output every time
```

---

## 🔧 Enable in Main Application

### Option 1: Config File (Recommended)

```bash
# Step 1: Setup
python run_mock_test.py --setup-only

# Step 2: Run
python main.py
```

### Option 2: Environment Variable

```bash
export MOCK_MODE=1
python main.py
```

### Option 3: Manual Integration

See [mock_integration_patch.py](mock_integration_patch.py) for 2 small code changes.

---

## 📚 Full Documentation

- **User Guide**: [MOCK_TESTING_GUIDE.md](MOCK_TESTING_GUIDE.md)
- **Integration**: [mock_integration_patch.py](mock_integration_patch.py)
- **Merge Strategy**: [MERGE_STRATEGY.md](MERGE_STRATEGY.md)
- **Complete Overview**: [MOCK_SYSTEM_SUMMARY.md](MOCK_SYSTEM_SUMMARY.md)

---

## 🐛 Something Wrong?

```bash
# Check you're in the right directory
pwd  # Should be /path/to/VALORANT-rank-yoinker

# Verify mock files exist
ls mock_*.py

# Test mock data generator
python -c "from mock_data import MockDataGenerator; print('✓ Works')"
```

Still having issues? See [MOCK_TESTING_GUIDE.md](MOCK_TESTING_GUIDE.md#troubleshooting)

---

## ✅ Expected Output

When you run `python run_mock_test.py --state ingame`, you should see:

```
============================================================
VALORANT Rank Yoinker - Mock Test Runner
============================================================
Game State: INGAME
[...]

[A formatted Rich table with colored text]:
- 10 players (5 per team)
- Proper rank names with colors (Iron 1-3, Bronze 1-3, Silver 1-3, Gold 1-3, Platinum 1-3, Diamond 1-3, Ascendant 1-3, Immortal 1-3, Radiant, Unranked)
- Team colors: Blue team (cyan), Red team (red)
- Stats: HS%, W/R, Level, RR, Peak Rank
- Agent assignments
- All colors match Windows VALORANT display

Match ID: [uuid]
Map: [map name]
Server: [server ID]
```

---

That's all you need to know! 🎮

**Want more?** Read the full guides above.

**Just want to test?** Run: `python run_mock_test.py`
