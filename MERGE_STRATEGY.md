# Merge Strategy for Mock System (macOS Development)

This document explains how to maintain the mock testing system when syncing with upstream updates, and which files will need attention during merges.

## Overview

The mock system is designed to minimize conflicts with upstream changes by keeping most functionality in separate, clearly-named files. However, some small modifications to core files are needed for integration.

---

## File Categories

### 🟢 NEW FILES (No Upstream Conflicts)

These files are custom additions that won't conflict with upstream:

#### Mock System Core
- `mock_data.py` - Mock data generator (700+ lines)
- `mock_requests.py` - Request interceptor (300+ lines)
- `mock_integration_patch.py` - Integration instructions
- `run_mock_test.py` - Standalone test runner (300+ lines)

#### Mock Data
- `mock_data/` - Directory for JSON scenarios
- `mock_data/README.md` - Mock data documentation

#### Documentation
- `MERGE_STRATEGY.md` - This file
- `.aimrules` - Development guide (no conflicts expected)
- `SYNC_WORKFLOW.md` - Git workflow guide (no conflicts expected)

**Merge Strategy**: These files can be safely kept in your fork. No action needed during upstream merges.

---

### 🟡 MODIFIED FILES (May Need Manual Merging)

These files have minimal modifications for mock mode integration:

#### src/constants.py
**Location**: Line ~220 in `DEFAULT_CONFIG` dict

**Modification**:
```python
"flags": {
    # ... existing flags ...
    "mock_mode": False,  # 🔧 CUSTOM: Enable mock mode for testing
}
```

**Merge Strategy**:
1. When upstream updates `DEFAULT_CONFIG`, merge normally
2. After merge, add the `"mock_mode": False` line back to the `flags` dict
3. This is a single-line addition, very low conflict risk

**Alternative**: Keep `mock_mode` in a separate config file and check for it at runtime

---

#### config.json
**Location**: Root directory

**Modification**:
```json
{
    "mock_mode": false,
    // ... rest of config ...
}
```

**Merge Strategy**:
- This is a user config file, not tracked in git (usually in .gitignore)
- No merge conflicts
- If you reset config, manually add `"mock_mode": false` back

---

#### main.py (OPTIONAL - See Alternatives Below)
**Location**: Lines ~40 (imports) and ~100 (Requests initialization)

**Modification 1** (after imports, ~line 40):
```python
# 🔧 CUSTOM: Mock mode support for macOS testing
try:
    from src.config import Config as ConfigCheck
    temp_cfg = ConfigCheck(lambda x: None)
    MOCK_MODE_ENABLED = temp_cfg.__dict__.get("mock_mode", False)
except:
    MOCK_MODE_ENABLED = False
```

**Modification 2** (Requests initialization, ~line 100):
```python
# 🔧 CUSTOM: Check for mock mode
if MOCK_MODE_ENABLED:
    from mock_requests import create_mock_requests
    Requests = create_mock_requests(version, log, ErrorSRC, game_state="MENUS")
    print("\n" + "=" * 60)
    print("MOCK MODE ACTIVE - Using simulated data")
    print("No VALORANT connection required (macOS testing)")
    print("=" * 60 + "\n")
else:
    Requests = Requests(version, log, ErrorSRC)
```

**Merge Strategy**:
1. **Before merging upstream**:
   - Note the exact line numbers where you added mock mode code
   - Save your modifications in a separate file

2. **During merge**:
   - If conflict occurs in main.py, resolve by accepting upstream version
   - After merge completes, re-apply the two modifications above

3. **After merge**:
   - Search for `Requests = Requests(version, log, ErrorSRC)` in main.py
   - Add the mock mode check around that line
   - Test that mock mode still works

**Conflict Likelihood**: LOW - These are small, localized additions that rarely conflict

---

### 🔵 ALTERNATIVE: Zero-Modification Integration

If you want to avoid modifying core files entirely, use environment variable detection:

**Step 1**: Don't modify main.py at all

**Step 2**: Create `mock_env.sh`:
```bash
#!/bin/bash
# Set environment variable to enable mock mode
export MOCK_MODE=1
python main.py
```

**Step 3**: Modify only `src/requestsV.py` at the very top:
```python
import os
if os.getenv("MOCK_MODE") == "1":
    # Replace this module's Requests class with mock version
    from mock_requests import MockRequests as Requests
```

This way, main.py is never touched, reducing merge conflicts to just one line in requestsV.py.

---

## Recommended Workflow for Upstream Merges

### Before Merging

1. **Verify mock mode works**:
   ```bash
   python run_mock_test.py --state ingame
   ```

2. **Document your modifications**:
   ```bash
   # Create a backup of your changes
   git diff > my_mock_modifications.patch
   ```

3. **Check which core files you modified**:
   ```bash
   git status
   git diff main.py
   git diff src/constants.py
   ```

### During Merge

1. **Fetch and merge upstream**:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. **If conflicts occur**:
   - Open conflicted files
   - Look for mock mode comments marked with `# 🔧 CUSTOM:`
   - Keep those sections, accept upstream for everything else

3. **Common conflict scenarios**:

   **Scenario A: DEFAULT_CONFIG changed**
   ```python
   <<<<<<< HEAD (your version)
   "flags": {
       "discord_rpc": True,
       "mock_mode": False,  # 🔧 CUSTOM
   }
   =======
   "flags": {
       "discord_rpc": True,
       "new_upstream_flag": False,
   }
   >>>>>>> upstream/main
   ```

   **Resolution**: Merge both, keep your mock_mode line:
   ```python
   "flags": {
       "discord_rpc": True,
       "new_upstream_flag": False,
       "mock_mode": False,  # 🔧 CUSTOM
   }
   ```

   **Scenario B: main.py import section changed**
   - Usually safe to keep both versions
   - Your mock imports don't conflict with upstream imports
   - Just ensure your mock mode check comes AFTER all imports

### After Merge

1. **Verify mock system still works**:
   ```bash
   python run_mock_test.py --state ingame
   ```

2. **Test with mock mode enabled**:
   ```bash
   # Enable mock mode in config.json
   python main.py
   ```

3. **Run normal mode (if on Windows/with VALORANT)**:
   ```bash
   # Disable mock mode in config.json
   python main.py
   ```

4. **If something broke**:
   ```bash
   # Re-apply your patch
   git apply my_mock_modifications.patch

   # Or manually re-add the mock code using mock_integration_patch.py
   cat mock_integration_patch.py  # Read instructions
   ```

---

## Maintenance Tips

### Keep Mock System Up to Date

1. **When upstream adds new API endpoints**:
   - Check if they're called by the application
   - Add mock responses in `mock_data.py` → `generate_mock_response()`
   - Test with `run_mock_test.py`

2. **When upstream changes data structures**:
   - Update mock generators in `mock_data.py`
   - Update sample responses to match new structure
   - Re-test all game states

3. **When upstream adds new features**:
   - Usually no changes needed if feature doesn't add API calls
   - If new API calls added, implement mock responses

### Testing After Upstream Updates

```bash
# 1. Test each game state
python run_mock_test.py --state menus
python run_mock_test.py --state pregame
python run_mock_test.py --state ingame

# 2. Test different scenarios
python run_mock_test.py --scenario mixed
python run_mock_test.py --scenario high_elo

# 3. Test with different seeds (verify randomness works)
python run_mock_test.py --seed 123
python run_mock_test.py --seed 456

# 4. Test full application (if possible)
python main.py  # with mock_mode: true in config.json
```

---

## Git Best Practices for Mock System

### Branch Strategy

1. **Keep mock system on a separate branch**:
   ```bash
   git checkout -b mock-system
   # Make all mock-related commits here
   ```

2. **Periodically merge upstream into mock branch**:
   ```bash
   git checkout mock-system
   git fetch upstream
   git merge upstream/main
   # Resolve conflicts
   git push origin mock-system
   ```

3. **Keep main branch clean** (optional):
   ```bash
   git checkout main
   git fetch upstream
   git merge upstream/main
   # main stays identical to upstream
   ```

### Commit Strategy

**DO**:
- Commit mock files separately from core modifications
- Use clear commit messages: `"Add mock system for macOS testing"`
- Tag mock-related commits: `[MOCK]` or `[CUSTOM]`

**DON'T**:
- Mix mock changes with other feature changes
- Commit mock_mode enabled in config.json (keep it local)

### Example Commit History

```
* 7a3f2e1 [MOCK] Add mock test scenarios
* 6b2d1c0 [MOCK] Create mock data generator
* 5a1b0f9 [MOCK] Add mock request interceptor
* 4c9e8d7 [MOCK] Integrate mock mode into main.py (2 lines)
* 3b8c7e6 [MOCK] Add mock_mode flag to constants.py (1 line)
* 2a7b6d5 Merge upstream/main
* 1c6e5f4 (upstream/main) Latest upstream commit
```

---

## Conflict Resolution Examples

### Example 1: main.py Import Changes

**Upstream adds new import**:
```python
# Upstream version:
from src.new_feature import NewFeature

# Your version:
if MOCK_MODE_ENABLED:
    from mock_requests import create_mock_requests
```

**Resolution**: Keep both
```python
from src.new_feature import NewFeature

if MOCK_MODE_ENABLED:
    from mock_requests import create_mock_requests
```

### Example 2: Requests Initialization Refactored

**Upstream moves Requests creation to a function**:
```python
# Upstream:
def initialize_requests(version, log, error):
    return Requests(version, log, error)

Requests = initialize_requests(version, log, ErrorSRC)
```

**Resolution**: Modify the function to support mock mode:
```python
def initialize_requests(version, log, error):
    # 🔧 CUSTOM: Check for mock mode
    if MOCK_MODE_ENABLED:
        from mock_requests import create_mock_requests
        return create_mock_requests(version, log, error)
    return Requests(version, log, error)

Requests = initialize_requests(version, log, ErrorSRC)
```

---

## Quick Reference

### Files to Watch During Merges

| File | Conflict Risk | Action if Conflict |
|------|---------------|-------------------|
| `main.py` | LOW | Re-apply 2 code blocks |
| `src/constants.py` | LOW | Re-add mock_mode flag |
| `config.json` | NONE | User config, not in git |
| `mock_*.py` | NONE | Your files, no conflict |
| `src/requestsV.py` | NONE | Usually not modified |

### Essential Commands

```bash
# Before merge: Save changes
git diff > mock_changes.patch

# Merge upstream
git fetch upstream && git merge upstream/main

# If conflicts: View them
git status
git diff --check

# After merge: Restore mock code if needed
# (Use mock_integration_patch.py as reference)

# Test mock system
python run_mock_test.py --state ingame

# Verify everything works
python main.py  # with mock_mode: true
```

---

## FAQ

**Q: Will mock mode affect normal operation?**
A: No. With `mock_mode: false` (default), the application works normally. Mock code is only imported when `mock_mode: true`.

**Q: What if upstream changes break my mock system?**
A: The mock system is isolated in separate files. Worst case, you update `mock_data.py` to match new API structures. The core application is unaffected.

**Q: Can I contribute mock mode to upstream?**
A: Possibly! The maintainer might appreciate macOS testing support. Create a clean PR with just the mock system files and minimal integration code.

**Q: Is there a way to avoid modifying main.py entirely?**
A: Yes! Use the environment variable approach (see "Alternative: Zero-Modification Integration" above). This keeps main.py pristine.

**Q: What if I accidentally push mock mode enabled?**
A: No problem - config.json shouldn't be in git. If it is, just commit a change setting it back to false.

---

## Summary

### Minimal Integration (Recommended)

**Only 2 files modified**:
1. `src/constants.py` - Add `"mock_mode": False` to flags (1 line)
2. `main.py` - Add mock mode check at Requests initialization (10 lines)

**All other files are new additions** with zero upstream conflicts.

### Zero Integration (Alternative)

**Only 1 file modified**:
1. `src/requestsV.py` - Add environment variable check (3 lines)

**Use**:
```bash
export MOCK_MODE=1 && python main.py
```

### Merge Workflow

1. Merge upstream normally
2. If conflicts, re-apply mock mode code (use `mock_integration_patch.py` as reference)
3. Test with `run_mock_test.py`
4. Done!

---

**Questions?** See `.aimrules` for detailed architecture information, or review `mock_integration_patch.py` for integration examples.
