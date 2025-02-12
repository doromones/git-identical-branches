#!/usr/bin/env python3
"""
git-identical-branches: A Git extension to find and manage local branches that have no changes
relative to a specified branch (by default, the current HEAD).

Provides subcommands:
  - list: Lists local branches that are fully contained in the reference (either by merge, rebase, or are identical).
  - delete-merged: Deletes branches that were merged via an actual merge commit.
  - delete-rebased: Deletes branches that were integrated without a merge commit (rebase/fast-forward).
  - delete-identical: Deletes branches that are exactly identical (same commit SHA) as the reference.

Use --help for more information.

Comments and output are in English locale.
"""

import argparse
import subprocess
import sys


def run_git_command(args, cwd=None):
    """
    Run a Git command and return its (stdout, stderr, exit_code).

    Raises subprocess.CalledProcessError if the command fails.
    """
    print(f"Running git command: {['git'] + args}")
    result = subprocess.run(["git"] + args, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, result.args, output=result.stdout, stderr=result.stderr
        )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def get_current_branch():
    """
    Return the name of the current branch.
    """
    stdout, _, _ = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    return stdout


def get_local_branches():
    """
    Return a list of all local branches, excluding HEAD or detached states.
    """
    stdout, _, _ = run_git_command(["branch", "--format=%(refname:short)"])
    branches = [b.strip() for b in stdout.split("\n") if b.strip()]
    return branches


def classify_branch(branch, reference):
    """
    Classify a branch relative to reference into one of:
      - "identical": Same commit SHA as reference
      - "merged": Branch is ancestor of reference AND there's at least one merge commit on reference that merges it
      - "rebased": Branch is ancestor of reference with no merge commits found that incorporate it
      - None: The branch is not fully contained in the reference or has diverged

    Returns:
      A string: "identical", "merged", "rebased", or None
    """
    # 1) Check if identical
    # rev-parse both commits
    ref_sha, _, _ = run_git_command(["rev-parse", reference])
    br_sha, _, _ = run_git_command(["rev-parse", branch])
    if ref_sha == br_sha:
        return "identical"

    # 2) Check if branch is ancestor of reference (fully contained in reference)
    # If branch is an ancestor, merge-base should be the branch's HEAD.
    merge_base, _, _ = run_git_command(["merge-base", branch, reference])
    if merge_base == br_sha:
        # The branch is contained in reference. Now let's see if there's a merge commit.
        # We'll look for merges in the range branch..reference.
        # If there's any merge in that range, we'll label it "merged".
        # Otherwise we'll label it "rebased".
        merges_log, _, _ = run_git_command(["log", f"{branch}..{reference}", "--merges", "--pretty=%H"])
        if merges_log.strip():
            return "merged"
        else:
            return "rebased"

    # Otherwise, it's not fully contained
    return None


def find_branches(reference):
    """
    Find branches fully contained in 'reference' (by default HEAD).
    Returns a dict with branch -> classification.

    classification in {"identical", "merged", "rebased"} or None
    """
    result = {}
    all_branches = get_local_branches()

    # If reference not in local_branches, it's likely HEAD or remote or something else, let's just trust it is valid
    for br in all_branches:
        if br == reference:
            # Skip the reference itself if listing all local branches
            continue
        classification = classify_branch(br, reference)
        result[br] = classification
    return result


def delete_branches(branches):
    """
    Safely delete the given branches using 'git branch -d <branch>'.
    Raises CalledProcessError if git refuses to delete (not fully merged, etc.).
    """
    for br in branches:
        print(f"Deleting branch '{br}'...")
        run_git_command(["branch", "-d", br])


def cmd_list(args):
    """
    List branches with no changes relative to reference, specifying how they were integrated:
    - identical (same SHA)
    - merged  (fully contained + merge commit found)
    - rebased (fully contained + no merge commit)
    """
    reference = args.reference or get_current_branch()
    print(f"Reference branch: {reference}")
    classified = find_branches(reference)
    for br, ctype in classified.items():
        if ctype is not None:
            print(f"{br} => {ctype}")


def cmd_delete_merged(args):
    """
    Delete branches that were integrated via a merge commit.
    """
    reference = args.reference or get_current_branch()
    classified = find_branches(reference)
    merged_branches = [br for br, ctype in classified.items() if ctype == "merged"]
    if not merged_branches:
        print("No merged branches found.")
        return
    delete_branches(merged_branches)


def cmd_delete_rebased(args):
    """
    Delete branches that were integrated without a merge commit (rebase or fast-forward).
    """
    reference = args.reference or get_current_branch()
    classified = find_branches(reference)
    rebased_branches = [br for br, ctype in classified.items() if ctype == "rebased"]
    if not rebased_branches:
        print("No rebased branches found.")
        return
    delete_branches(rebased_branches)


def cmd_delete_identical(args):
    """
    Delete branches that are identical (same commit SHA) to reference.
    """
    reference = args.reference or get_current_branch()
    classified = find_branches(reference)
    identical_branches = [br for br, ctype in classified.items() if ctype == "identical"]
    if not identical_branches:
        print("No identical branches found.")
        return
    delete_branches(identical_branches)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "git-identical-branches: A Git extension to find and manage local branches "
            "that have no changes relative to a specified branch (by default, HEAD)."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # common argument for reference
    common_args = argparse.ArgumentParser(add_help=False)
    common_args.add_argument(
        "reference",
        nargs="?",
        default=None,
        help="Reference branch to compare against (default: current HEAD).",
    )

    # list
    list_parser = subparsers.add_parser(
        "list",
        parents=[common_args],
        help="List local branches that are fully contained in the reference (with classification).",
    )
    list_parser.set_defaults(func=cmd_list)

    # delete-merged
    delete_merged_parser = subparsers.add_parser(
        "delete-merged",
        parents=[common_args],
        help="Delete local branches that were integrated via a merge commit.",
    )
    delete_merged_parser.set_defaults(func=cmd_delete_merged)

    # delete-rebased
    delete_rebased_parser = subparsers.add_parser(
        "delete-rebased",
        parents=[common_args],
        help="Delete local branches that were integrated without a merge commit (rebase/fast-forward).",
    )
    delete_rebased_parser.set_defaults(func=cmd_delete_rebased)

    # delete-identical
    delete_identical_parser = subparsers.add_parser(
        "delete-identical",
        parents=[common_args],
        help="Delete local branches that are identical (same SHA) to the reference.",
    )
    delete_identical_parser.set_defaults(func=cmd_delete_identical)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

    # try:
    #     args.func(args)
    # except subprocess.CalledProcessError as e:
    #     print(f"Error: {e.stderr.strip() or e.output.strip()}", file=sys.stderr)
    #     sys.exit(e.returncode)


if __name__ == "__main__":
    main()