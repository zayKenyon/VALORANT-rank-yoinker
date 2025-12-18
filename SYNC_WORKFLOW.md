# Fork Sync Workflow for VALORANT Rank Yoinker

This guide explains how to maintain your fork of the VALORANT-rank-yoinker repository, sync with upstream changes, and contribute back to the project.

## Table of Contents
- [Initial Setup](#initial-setup)
- [Daily Workflow](#daily-workflow)
- [Syncing with Upstream](#syncing-with-upstream)
- [Branching Strategy](#branching-strategy)
- [Handling Merge Conflicts](#handling-merge-conflicts)
- [Contributing Back](#contributing-back)
- [Common Commands Reference](#common-commands-reference)
- [Troubleshooting](#troubleshooting)

---

## Initial Setup

### Step 1: Fork the Repository

1. Go to https://github.com/zayKenyon/VALORANT-rank-yoinker
2. Click the **"Fork"** button in the top-right corner
3. Select your account as the destination
4. Wait for GitHub to create your fork

### Step 2: Clone Your Fork

```bash
# Clone YOUR fork (not the original repo)
git clone https://github.com/YOUR_USERNAME/VALORANT-rank-yoinker.git
cd VALORANT-rank-yoinker
```

**Note**: Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3: Add Upstream Remote

The "upstream" remote points to the original repository so you can pull in updates:

```bash
# Add the original repo as "upstream"
git remote add upstream https://github.com/zayKenyon/VALORANT-rank-yoinker.git

# Verify your remotes
git remote -v
```

You should see:
```
origin    https://github.com/YOUR_USERNAME/VALORANT-rank-yoinker.git (fetch)
origin    https://github.com/YOUR_USERNAME/VALORANT-rank-yoinker.git (push)
upstream  https://github.com/zayKenyon/VALORANT-rank-yoinker.git (fetch)
upstream  https://github.com/zayKenyon/VALORANT-rank-yoinker.git (push)
```

### Step 4: Set Up Your Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Test the application
python main.py
```

---

## Daily Workflow

### Before Starting New Work

Always sync with upstream before starting new features:

```bash
# 1. Switch to main branch
git checkout main

# 2. Fetch latest changes from upstream
git fetch upstream

# 3. Merge upstream changes into your main
git merge upstream/main

# 4. Push updates to your fork
git push origin main

# 5. Create a new feature branch
git checkout -b feature/your-feature-name
```

### While Working

```bash
# Make changes to files
# ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature X that does Y"

# Push to your fork
git push origin feature/your-feature-name
```

### When Feature is Complete

```bash
# Make sure you're on your feature branch
git checkout feature/your-feature-name

# Pull latest upstream changes and rebase (optional but recommended)
git fetch upstream
git rebase upstream/main

# Push to your fork (may need --force if rebased)
git push origin feature/your-feature-name --force-with-lease

# Go to GitHub and create Pull Request
```

---

## Syncing with Upstream

### Quick Sync (Recommended Method)

```bash
# Fetch all upstream changes
git fetch upstream

# Switch to your main branch
git checkout main

# Merge upstream/main into your main
git merge upstream/main

# Push updated main to your fork
git push origin main
```

### Alternative: Rebase Method

```bash
# Fetch upstream changes
git fetch upstream

# Switch to main
git checkout main

# Rebase your main on top of upstream/main
git rebase upstream/main

# Force push to your fork (since history changed)
git push origin main --force-with-lease
```

**When to use which**:
- **Merge**: Safer, preserves history, recommended for main branch
- **Rebase**: Cleaner history, use for feature branches before PR

### Syncing a Feature Branch

If you're working on a feature branch and upstream has changed:

```bash
# On your feature branch
git fetch upstream
git rebase upstream/main

# Or, if you prefer merging:
git merge upstream/main

# Resolve conflicts if any (see below)

# Push (may need --force-with-lease if rebased)
git push origin feature/your-feature-name --force-with-lease
```

---

## Branching Strategy

### Branch Naming Convention

Use descriptive names with prefixes:

- `feature/add-weapon-stats` - New features
- `fix/rank-display-bug` - Bug fixes
- `refactor/optimize-api-calls` - Code improvements
- `docs/update-readme` - Documentation
- `test/add-unit-tests` - Testing

### Creating Branches

```bash
# Always branch from updated main
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

### Deleting Merged Branches

After your PR is merged:

```bash
# Delete local branch
git branch -d feature/your-feature-name

# Delete remote branch on your fork
git push origin --delete feature/your-feature-name
```

---

## Handling Merge Conflicts

Conflicts occur when the same code is changed in both your fork and upstream.

### Step-by-Step Conflict Resolution

1. **Fetch and attempt merge**:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. **Git will notify you of conflicts**:
   ```
   Auto-merging main.py
   CONFLICT (content): Merge conflict in main.py
   Automatic merge failed; fix conflicts and then commit the result.
   ```

3. **View conflicted files**:
   ```bash
   git status
   ```

4. **Open conflicted files** - Look for conflict markers:
   ```python
   <<<<<<< HEAD
   # Your changes
   print("Your version")
   =======
   # Upstream changes
   print("Upstream version")
   >>>>>>> upstream/main
   ```

5. **Resolve the conflict** - Edit the file to keep the correct code:
   ```python
   # Keep what you want, remove conflict markers
   print("Final version")
   ```

6. **Mark as resolved**:
   ```bash
   git add main.py
   ```

7. **Complete the merge**:
   ```bash
   git commit -m "Merge upstream changes, resolve conflicts in main.py"
   ```

8. **Push to your fork**:
   ```bash
   git push origin your-branch-name
   ```

### Aborting a Merge

If you want to start over:

```bash
git merge --abort
```

### Tools for Resolving Conflicts

- **VS Code**: Built-in merge conflict resolver
- **Command line**: `git mergetool` (if configured)
- **Manual**: Edit files directly

---

## Contributing Back

### Creating a Pull Request

1. **Push your feature branch to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Go to GitHub**:
   - Visit your fork: `https://github.com/YOUR_USERNAME/VALORANT-rank-yoinker`
   - Click "Compare & pull request" button
   - Or go to "Pull requests" tab → "New pull request"

3. **Fill out PR template**:
   - **Base repository**: `zayKenyon/VALORANT-rank-yoinker`
   - **Base branch**: `main`
   - **Head repository**: `YOUR_USERNAME/VALORANT-rank-yoinker`
   - **Compare branch**: `feature/your-feature-name`

4. **Write clear PR description**:
   ```markdown
   ## Summary
   Brief description of what this PR does

   ## Changes
   - Added feature X
   - Fixed bug Y
   - Updated documentation Z

   ## Testing
   - Tested in INGAME state
   - Tested with party members
   - Tested Discord RPC integration

   ## Screenshots (if applicable)
   [Add screenshots]
   ```

5. **Submit pull request**

### PR Best Practices

- **One PR per feature**: Don't mix unrelated changes
- **Small commits**: Break large changes into reviewable chunks
- **Test thoroughly**: Ensure all game states work
- **Update documentation**: If you change functionality, update docs
- **Respond to feedback**: Address review comments promptly

---

## Common Commands Reference

### Repository Status

```bash
# Check current branch and status
git status

# View commit history
git log --oneline --graph

# See what branches exist
git branch -a

# See differences
git diff
```

### Syncing

```bash
# Quick sync with upstream
git fetch upstream && git merge upstream/main && git push origin main

# Update feature branch with latest upstream
git checkout feature/branch && git rebase upstream/main
```

### Cleaning Up

```bash
# Delete local branch
git branch -d branch-name

# Delete remote branch on your fork
git push origin --delete branch-name

# Discard local changes (careful!)
git checkout -- filename
git reset --hard HEAD  # Discard ALL local changes
```

### Stashing Changes

```bash
# Save work in progress without committing
git stash

# List stashes
git stash list

# Restore stashed changes
git stash pop

# Discard stashed changes
git stash drop
```

---

## Troubleshooting

### "Diverged Branches" Error

**Problem**: Your main and upstream/main have diverged.

**Solution**:
```bash
git checkout main
git fetch upstream
git reset --hard upstream/main  # WARNING: Loses local commits on main
git push origin main --force-with-lease
```

### "Already Up to Date" But Fork is Behind

**Problem**: GitHub shows your fork is behind, but git says up to date.

**Solution**:
```bash
# Fetch all updates
git fetch upstream

# Hard reset to upstream
git checkout main
git reset --hard upstream/main
git push origin main --force-with-lease
```

### Can't Push to Origin

**Problem**: `git push origin main` fails.

**Check**:
1. Are you authenticated with GitHub?
   ```bash
   git remote -v  # Check if URL is correct
   ```

2. Do you have write access to your fork? (Should always be yes)

3. Is branch protected?
   ```bash
   git push origin main --force-with-lease  # If needed
   ```

### Accidentally Committed to Main

**Problem**: Made commits to `main` instead of feature branch.

**Solution**:
```bash
# Create branch with current changes
git branch feature/my-fix

# Reset main to upstream
git checkout main
git reset --hard upstream/main

# Switch to feature branch
git checkout feature/my-fix

# Push feature branch
git push origin feature/my-fix
```

### Large Merge Conflicts

**Problem**: Too many conflicts to resolve manually.

**Solution**:
```bash
# Abort current merge
git merge --abort

# Create new branch from upstream
git checkout -b fix/merge-conflicts upstream/main

# Cherry-pick your changes one by one
git cherry-pick <commit-hash>

# Or recreate changes manually
```

### Force Push Safety

Always use `--force-with-lease` instead of `--force`:

```bash
# SAFE: Won't overwrite if remote changed
git push origin branch --force-with-lease

# DANGEROUS: Overwrites remote regardless
git push origin branch --force  # Avoid unless necessary
```

---

## Workflow Diagram

```
┌─────────────────┐
│ zayKenyon/      │
│ VALORANT-rank-  │  ← Upstream (original repo)
│ yoinker         │
└────────┬────────┘
         │
         │ Fork
         ↓
┌─────────────────┐
│ YOUR_USERNAME/  │
│ VALORANT-rank-  │  ← Origin (your fork)
│ yoinker         │
└────────┬────────┘
         │
         │ Clone
         ↓
┌─────────────────┐
│ Local           │
│ Repository      │  ← Your machine
└─────────────────┘

Workflow:
1. Fetch upstream → Merge → Push to origin
2. Create feature branch → Work → Push to origin
3. Create PR from origin to upstream
```

---

## Additional Resources

- [GitHub Docs: Syncing a Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork)
- [Git Branching Best Practices](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)
- [Understanding Git Rebase](https://git-scm.com/docs/git-rebase)
- [Resolving Merge Conflicts](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line)

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Sync fork with upstream | `git fetch upstream && git merge upstream/main` |
| Create feature branch | `git checkout -b feature/name` |
| Push to your fork | `git push origin branch-name` |
| Update feature branch | `git rebase upstream/main` |
| Undo last commit | `git reset --soft HEAD~1` |
| Discard all changes | `git reset --hard HEAD` |
| View remote URLs | `git remote -v` |
| Delete branch | `git branch -d branch-name` |
| Stash changes | `git stash` |
| Apply stash | `git stash pop` |

---

**Happy Contributing!** 🎮

For questions or issues, join the [Discord community](https://discord.gg/HeTKed64Ka).
