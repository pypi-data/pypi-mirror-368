import subprocess

def run_git_command(args, cwd='.'):
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if e.stderr and 'not a git repository' in e.stderr.lower():
            print("Error: The directory is not a git repository.")
        else:
            print(f"Git command error: {e.stderr.strip() if e.stderr else e}")
        return None

def get_current_branch(repo_path='.'):
    # Returns current branch name or None if detached HEAD
    branch = run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_path)
    if branch == 'HEAD':
        return None  # detached HEAD
    return branch

def get_branch_ahead_behind(repo_path='.'):
    # Returns a tuple (ahead, behind) counts of commits compared to remote tracking branch
    status = run_git_command(['status', '-sb'], cwd=repo_path)
    if status is None:
        return None, None
    # status example first line:
    # ## main...origin/main [ahead 1, behind 2]
    first_line = status.splitlines()[0]
    import re
    m = re.search(r'\[ahead (\d+), behind (\d+)\]', first_line)
    if m:
        ahead = int(m.group(1))
        behind = int(m.group(2))
        return ahead, behind
    m = re.search(r'\[ahead (\d+)\]', first_line)
    if m:
        ahead = int(m.group(1))
        return ahead, 0
    m = re.search(r'\[behind (\d+)\]', first_line)
    if m:
        behind = int(m.group(1))
        return 0, behind
    # no ahead/behind info means branch is in sync
    return 0, 0

def parse_git_status(repo_path='.'):
    output = run_git_command(['status', '--porcelain'], cwd=repo_path)
    if output is None:
        return None

    staged = 0
    unstaged = 0
    untracked = 0

    for line in output.splitlines():
        if not line:
            continue
        status = line[:2]
        if status[0] != ' ':
            staged += 1
        if status[1] != ' ':
            unstaged += 1
        if status == '??':
            untracked += 1

    branch = get_current_branch(repo_path)
    ahead, behind = get_branch_ahead_behind(repo_path)

    return {
        'staged': staged,
        'unstaged': unstaged,
        'untracked': untracked,
        'branch': branch,
        'ahead': ahead,
        'behind': behind,
    }

def get_staged_files(repo_path='.'):
    """Return a list of staged files."""
    output = run_git_command(['diff', '--name-only', '--staged'], cwd=repo_path)
    if output is None:
        return []
    return output.splitlines()

def generate_commit_message(repo_path='.'):
    staged_files = get_staged_files(repo_path)
    if not staged_files:
        return "No staged changes to commit."

    # Basic heuristics: collect file extensions/types
    exts = {}
    for f in staged_files:
        ext = f.split('.')[-1] if '.' in f else 'other'
        exts[ext] = exts.get(ext, 0) + 1

    # Simple templates based on file types
    parts = []
    if 'py' in exts:
        parts.append("Update Python code")
    if 'md' in exts or 'rst' in exts:
        parts.append("Update documentation")
    if 'js' in exts or 'ts' in exts:
        parts.append("Update JavaScript code")
    if 'css' in exts or 'scss' in exts:
        parts.append("Update stylesheets")
    if not parts:
        parts.append("Update project files")

    # Add number of files changed
    msg = f"{', '.join(parts)} ({len(staged_files)} files)"
    return msg

def run_git_command_capture_output(args, cwd='.'):
    """Run a git command, return (success:bool, stdout:str, stderr:str)."""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return True, result.stdout.strip(), ""
    except subprocess.CalledProcessError as e:
        return False, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else str(e)

def is_working_directory_clean(repo_path='.'):
    output = run_git_command(['status', '--porcelain'], cwd=repo_path)
    return output == ''

def has_merge_conflicts(repo_path='.'):
    # Check if there are unresolved conflicts
    output = run_git_command(['diff', '--name-only', '--diff-filter=U'], cwd=repo_path)
    return bool(output)

def git_sync(repo_path='.'):
    if not is_working_directory_clean(repo_path):
        print("⚠️  Working directory is not clean. Please commit or stash changes before syncing.")
        return

    print("Fetching from remote...")
    success, out, err = run_git_command_capture_output(['fetch'], cwd=repo_path)
    if not success:
        print(f"Fetch failed:\n{err}")
        return

    branch = get_current_branch(repo_path)
    if not branch:
        print("Cannot sync: detached HEAD state.")
        return

    remote_branch = f'origin/{branch}'

    print(f"Rebasing {branch} onto {remote_branch}...")
    success, out, err = run_git_command_capture_output(['rebase', remote_branch], cwd=repo_path)
    if not success:
        print("Rebase failed. Possible conflicts detected.")
        if has_merge_conflicts(repo_path):
            print("Merge conflicts found.")
            while True:
                choice = input("[R]etry after resolving conflicts, [A]bort rebase, [E]xit sync: ").strip().lower()
                if choice == 'r':
                    print("Please resolve conflicts, then run 'git rebase --continue' manually, then rerun sync.")
                    break
                elif choice == 'a':
                    print("Aborting rebase...")
                    abort_success, _, abort_err = run_git_command_capture_output(['rebase', '--abort'], cwd=repo_path)
                    if abort_success:
                        print("Rebase aborted.")
                    else:
                        print(f"Failed to abort rebase:\n{abort_err}")
                    break
                elif choice == 'e':
                    print("Exiting sync command.")
                    break
                else:
                    print("Invalid choice. Please enter R, A, or E.")
        else:
            print(err)
        return

    print("Pushing changes to remote...")
    success, out, err = run_git_command_capture_output(['push'], cwd=repo_path)
    if not success:
        print(f"Push failed:\n{err}")
        return

    print("Sync complete!")
