#!/usr/bin/env python3
import subprocess
import sys

def run_git_command(*args):
    """Run a git command and return its output"""
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()

def get_current_branch():
    """Get the name of the current branch"""
    return run_git_command("rev-parse", "--abbrev-ref", "HEAD")

def get_local_branches():
    """Get a list of all local branches"""
    return run_git_command("branch").replace("*", "").split()

def get_merged_branches(base_branch):
    """Get branches that are merged into the base branch"""
    return set(run_git_command("branch", "--merged", base_branch).replace("*", "").split())

def get_rebased_branches(base_branch):
    """Get branches that are rebased onto the base branch"""
    base_commit = run_git_command("rev-parse", base_branch)
    branches = get_local_branches()
    rebased = []
    for branch in branches:
        if branch == base_branch:
            continue
        branch_commit = run_git_command("merge-base", base_branch, branch)
        if branch_commit == base_commit:
            rebased.append(branch)
    return set(rebased)

def get_identical_branches(base_branch):
    """Get branches that are identical to the base branch"""
    base_commit = run_git_command("rev-parse", base_branch)
    return {branch for branch in get_local_branches() if branch != base_branch and run_git_command("rev-parse", branch) == base_commit}

def delete_branches(branches):
    """Delete the given branches"""
    for branch in branches:
        subprocess.run(["git", "branch", "-d", branch])
        print(f"Deleted branch: {branch}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Find and remove branches without changes relative to a base branch.")
    parser.add_argument("base", nargs="?", default=get_current_branch(), help="Base branch to compare against (default: current branch)")
    parser.add_argument("--merged", action="store_true", help="Show branches merged into the base branch")
    parser.add_argument("--rebased", action="store_true", help="Show branches rebased onto the base branch")
    parser.add_argument("--identical", action="store_true", help="Show branches identical to the base branch")
    parser.add_argument("--delete-merged", action="store_true", help="Delete merged branches")
    parser.add_argument("--delete-rebased", action="store_true", help="Delete rebased branches")
    parser.add_argument("--delete-identical", action="store_true", help="Delete identical branches")
    args = parser.parse_args()

    base_branch = args.base
    if args.merged or args.delete_merged:
        merged_branches = get_merged_branches(base_branch)
        if args.delete_merged:
            delete_branches(merged_branches)
        else:
            print("Merged branches:", merged_branches)

    if args.rebased or args.delete_rebased:
        rebased_branches = get_rebased_branches(base_branch)
        if args.delete_rebased:
            delete_branches(rebased_branches)
        else:
            print("Rebased branches:", rebased_branches)

    if args.identical or args.delete_identical:
        identical_branches = get_identical_branches(base_branch)
        if args.delete_identical:
            delete_branches(identical_branches)
        else:
            print("Identical branches:", identical_branches)

if __name__ == "__main__":
    main()
