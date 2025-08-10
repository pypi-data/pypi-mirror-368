from gitbotx.repo import parse_git_status, generate_commit_message, git_sync

def suggest_commands(status):
    if status is None:
        print("Not a git repository or git not installed.")
        return

    staged = status['staged']
    unstaged = status['unstaged']
    untracked = status['untracked']
    branch = status.get('branch')
    ahead = status.get('ahead', 0)
    behind = status.get('behind', 0)

    print(f"On branch: {branch if branch else 'DETACHED HEAD'}")

    if unstaged > 0:
        print(f"You have {unstaged} unstaged changes. Consider running:\n  git add .")
    if staged > 0:
        print(f"You have {staged} staged changes ready to commit. Consider running:\n  git commit")
    if untracked > 0:
        print(f"You have {untracked} untracked files. Consider running:\n  git add <file>")

    if ahead > 0 and behind > 0:
        print(f"Your branch and remote have diverged.\nResolve with:\n  git pull --rebase\n  git push")
    elif ahead > 0:
        print(f"Your branch is ahead of remote by {ahead} commits.\nYou can push your changes:\n  git push")
    elif behind > 0:
        print(f"Your branch is behind remote by {behind} commits.\nYou should update your branch:\n  git pull --rebase")
    else:
        if staged == 0 and unstaged == 0 and untracked == 0:
            print("Working directory clean and branch is up-to-date.")

def commit_message_command(repo_path='.'):
    msg = generate_commit_message(repo_path)
    print("Suggested commit message:")
    print(f"  {msg}")

def sync_command(repo_path='.'):
    git_sync(repo_path)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Context-Aware Git Helper CLI")
    parser.add_argument('--status', action='store_true', help='Show git status summary and suggestions')
    parser.add_argument('--commit-msg', action='store_true', help='Generate basic commit message suggestion')
    parser.add_argument('--sync', action='store_true', help='Fetch, rebase, and push changes to remote')
    parser.add_argument('--repo', type=str, default='.', help='Path to the git repository (default: current directory)')
    args = parser.parse_args()

    if args.status:
        status = parse_git_status(args.repo)
        suggest_commands(status)
    elif args.commit_msg:
        commit_message_command(args.repo)
    elif args.sync:
        sync_command(args.repo)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
