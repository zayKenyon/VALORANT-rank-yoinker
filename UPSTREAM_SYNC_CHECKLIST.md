# Upstream Sync Checklist

Quick reference for syncing your fork with upstream updates.

---

## Before You Start

- [ ] Ensure all local changes are committed or stashed
- [ ] Run verification tests: `bash verify_mock_system.sh`
- [ ] Note current commit: `git log -1 --oneline`

---

## Step 1: Fetch Upstream Changes

```bash
git fetch upstream
```

---

## Step 2: Review Changes

```bash
# See what's new
git log HEAD..upstream/main --oneline

# Detailed view
git log HEAD..upstream/main --stat

# Visual branch comparison
git log --oneline --all --graph --decorate -20
```

**Look for**:
- API endpoint changes
- Presence data structure changes
- Loadout/skins API changes
- New dependencies
- Breaking changes

---

## Step 3: Create Backup Branch

```bash
# Always create a backup before merging
git checkout -b backup-before-sync-$(date +%Y-%m-%d)
git checkout main
```

---

## Step 4: Analyze Impact

Check which files changed:
```bash
git diff --stat HEAD..upstream/main
```

### Files to Watch

**Core Integration Points** (if you've integrated mock mode):
- [ ] `main.py` - Check Requests initialization
- [ ] `src/constants.py` - Check DEFAULT_CONFIG

**API-Related Files** (may affect mock data):
- [ ] `src/presences.py` - Presence API structure
- [ ] `src/Loadouts.py` - Skins/loadouts API
- [ ] `src/requestsV.py` - Request handling
- [ ] `main.py` - Game state handling

**Low Risk Files** (unlikely to affect mock):
- [ ] `src/colors.py` - Display colors only
- [ ] `src/table.py` - Display formatting
- [ ] `src/rpc.py` - Discord RPC
- [ ] Documentation files

---

## Step 5: Merge Upstream

```bash
git merge upstream/main
```

### If No Conflicts
✅ Proceed to testing

### If Conflicts Occur

**Common Conflict Scenarios**:

#### Scenario A: main.py Requests initialization
```python
<<<<<<< HEAD (your version)
if MOCK_MODE_ENABLED:
    from mock_requests import create_mock_requests
    Requests = create_mock_requests(version, log, ErrorSRC)
else:
    Requests = Requests(version, log, ErrorSRC)
=======
Requests = Requests(version, log, ErrorSRC, new_parameter)
>>>>>>> upstream/main
```

**Resolution**: Keep both, add new parameter to mock:
```python
if MOCK_MODE_ENABLED:
    from mock_requests import create_mock_requests
    Requests = create_mock_requests(version, log, ErrorSRC, new_parameter)
else:
    Requests = Requests(version, log, ErrorSRC, new_parameter)
```

#### Scenario B: src/constants.py DEFAULT_CONFIG
```python
<<<<<<< HEAD
"flags": {
    "discord_rpc": True,
    "mock_mode": False,  # Your addition
}
=======
"flags": {
    "discord_rpc": True,
    "new_upstream_flag": False,
}
>>>>>>> upstream/main
```

**Resolution**: Merge both:
```python
"flags": {
    "discord_rpc": True,
    "new_upstream_flag": False,
    "mock_mode": False,  # Your addition
}
```

---

## Step 6: Update Mock System

### Check API Structure Changes

```bash
# Compare presence handling
git diff HEAD^..HEAD src/presences.py
git diff HEAD^..HEAD main.py | grep -A 5 -B 5 presence

# Compare loadout handling
git diff HEAD^..HEAD src/Loadouts.py
```

### Update mock_data.py If Needed

**Common updates needed**:

1. **New API endpoints**:
   ```python
   # Add to generate_mock_response() in mock_data.py
   elif "/new-endpoint/" in endpoint:
       return {"data": {...}}
   ```

2. **Changed response structure**:
   ```python
   # Update the relevant generator function
   def generate_some_data(self):
       return {
           "newField": "value",  # Add new fields
           # Keep existing fields
       }
   ```

3. **New presence structure**:
   ```python
   # Update generate_presence_data() if needed
   ```

---

## Step 7: Test Everything

### Quick Test
```bash
bash verify_mock_system.sh
```

### Detailed Tests
```bash
# Test all game states
python3 run_mock_test.py --state menus
python3 run_mock_test.py --state pregame
python3 run_mock_test.py --state ingame

# Test all scenarios
python3 run_mock_test.py --scenario mixed
python3 run_mock_test.py --scenario high_elo
python3 run_mock_test.py --scenario new_players

# Test reproducibility
python3 run_mock_test.py --seed 42
python3 run_mock_test.py --seed 42  # Should be identical
```

### Full Application Test (if integrated)
```bash
# With mock mode
python main.py  # config.json should have "mock_mode": true

# Without mock mode (if VALORANT available)
# Edit config.json: "mock_mode": false
python main.py
```

---

## Step 8: Update Documentation

### Update .aimrules (if needed)
- [ ] New API endpoints
- [ ] Changed data structures
- [ ] New game states
- [ ] Modified request patterns

### Update SYNC_REPORT.md
- [ ] Document what changed
- [ ] Note any conflicts and resolutions
- [ ] List files modified
- [ ] Record test results

### Update MOCK_TESTING_GUIDE.md (if needed)
- [ ] New test scenarios
- [ ] Changed API behavior
- [ ] New troubleshooting tips

---

## Step 9: Commit and Push

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Sync with upstream: [brief description of changes]

- Merged upstream/main commit [hash]
- Updated mock system for [changes]
- All tests passing
"

# Push to your fork
git push origin main
```

---

## Step 10: Clean Up

```bash
# Delete backup branch (if everything works)
git branch -d backup-before-sync-YYYY-MM-DD

# Or keep it for safety until next sync
```

---

## Troubleshooting

### Issue: Mock tests failing after merge

**Diagnosis**:
```bash
# Check what changed in test files
git diff HEAD~1 main.py src/presences.py src/Loadouts.py

# Run with verbose output
python3 run_mock_test.py --state ingame 2>&1 | tee debug.log
```

**Common fixes**:
1. Update mock_data.py response structures
2. Update mock_requests.py endpoint handling
3. Check for new required parameters

### Issue: Conflicts in main.py

**Quick fix**:
```bash
# Accept upstream version
git checkout --theirs main.py

# Re-apply mock mode integration
# Copy from mock_integration_patch.py
```

### Issue: Upstream broke something

**Rollback**:
```bash
# Restore from backup
git checkout backup-before-sync-YYYY-MM-DD
git checkout -b main-rollback
git push origin main-rollback

# Investigate issue
# Once fixed, merge again
```

---

## Quick Commands Reference

```bash
# Status check
git fetch upstream && git log HEAD..upstream/main --oneline

# Safe merge with backup
git checkout -b backup-$(date +%Y-%m-%d) && git checkout main && git merge upstream/main

# Test suite
bash verify_mock_system.sh && python3 run_mock_test.py --state ingame

# Full workflow
git fetch upstream && \
git checkout -b backup-$(date +%Y-%m-%d) && \
git checkout main && \
git merge upstream/main && \
bash verify_mock_system.sh && \
git push origin main
```

---

## When to Sync

### Regular Schedule
- 🗓️ **Monthly**: Check for updates
- 🗓️ **Quarterly**: Perform sync even if no major changes

### Event-Based
- 🔔 **Version bump**: When upstream version changes (e.g., 2.91 → 2.92)
- 🚨 **Security updates**: Dependabot PRs or security announcements
- ✨ **New features**: When upstream announces major features
- 🐛 **Bug fixes**: When bugs you've encountered are fixed upstream
- 📡 **API changes**: When Riot updates their API (watch for issues in upstream)

### Warning Signs to Sync Soon
- ⚠️ Upstream has >10 commits since your last sync
- ⚠️ Multiple PRs about API structure changes
- ⚠️ Issues mentioning crashes or errors you haven't seen
- ⚠️ Dependencies are outdated (requirements.txt changes)

---

## Success Criteria

After sync, you should have:

- ✅ All 8 mock verification tests passing
- ✅ All 3 game states displaying correctly (menus, pregame, ingame)
- ✅ Colors rendering properly in terminal
- ✅ Proper rank names (Iron 1-3, Bronze 1-3, etc.)
- ✅ No Python errors or warnings
- ✅ SYNC_REPORT.md updated
- ✅ Git history clean (no merge artifacts)

---

## Notes

- **Never force push** unless you're certain and alone on the fork
- **Always test before pushing** - your fork is your safety net
- **Document conflicts** - they'll help next time
- **Keep backups** until you're 100% confident
- **Mock system isolation is your friend** - leverages it to avoid conflicts

---

## Contact Points

- **Upstream Issues**: https://github.com/zayKenyon/VALORANT-rank-yoinker/issues
- **Your Fork**: https://github.com/[yourusername]/VALORANT-rank-yoinker
- **Mock System Docs**: See MOCK_TESTING_GUIDE.md, MERGE_STRATEGY.md

---

**Last Updated**: 2025-12-18
**Current Upstream Commit**: d2bd40e
**Sync Status**: ✅ In Sync
