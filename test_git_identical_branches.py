#!/usr/bin/env python3
"""
Tests for git-identical-branches.py

The tests create a temporary directory, initialize a Git repository, perform some
branching and commit operations, then run the git-identical-branches.py script
to verify its behavior.

After the tests (or if an error occurs), the test directory is removed.
"""

import unittest
import tempfile
import shutil
import subprocess
import os


SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "git-identical-branches.py"))

def run_command(cmd, cwd=None):
    """
    Helper to run a command in a subprocess.
    Raises subprocess.CalledProcessError if return code != 0.
    Returns (stdout, stderr).
    """
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=result.args,
            output=result.stdout,
            stderr=result.stderr,
        )
    return (result.stdout.strip(), result.stderr.strip())


class TestGitIdenticalBranches(unittest.TestCase):
    def setUp(self):
        """
        Create a temporary directory and initialize a Git repository for testing.
        """
        self.test_dir = tempfile.mkdtemp(prefix="git-identical-branches-test-")
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        run_command(["git", "init"])

        # Create an initial commit on 'main'
        with open("file.txt", "w") as f:
            f.write("initial")
        run_command(["git", "add", "file.txt"])
        run_command(["git", "commit", "-m", "Initial commit"])

    def tearDown(self):
        """
        Remove the temporary directory and return to the original working directory.
        """
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_identical_branch(self):
        """
        Test that a branch with the same commit SHA is reported as identical.
        """
        # Create a branch with the same commit
        run_command(["git", "checkout", "-b", "identical-branch"])
        # Do nothing, it's the same commit as main
        run_command(["git", "checkout", "main"])

        # Run the "list" command
        cmd = ["python3", SCRIPT_PATH, "list", "main"]
        stdout, _ = run_command(cmd)
        # We expect to see that 'identical-branch' is "identical"
        self.assertIn("identical-branch => identical", stdout)

    def test_merged_branch(self):
        """
        Test that a branch merged into main is reported as merged.
        """
        # Create a branch and commit something
        run_command(["git", "checkout", "-b", "feature-merged"])
        with open("feature.txt", "w") as f:
            f.write("feature content")
        run_command(["git", "add", "feature.txt"])
        run_command(["git", "commit", "-m", "Add feature"])
        # Merge into main
        run_command(["git", "checkout", "main"])
        run_command(["git", "merge", "feature-merged", "--no-edit"])

        # Run the "list" command
        cmd = ["python3", SCRIPT_PATH, "list", "main"]
        stdout, _ = run_command(cmd)
        # We expect to see that 'feature-merged' => merged
        self.assertIn("feature-merged => merged", stdout)

    def test_rebased_branch(self):
        """
        Test that a branch integrated via rebase (no merge commit) is reported as rebased.
        We'll do a fast-forward rebase for simplicity.
        """
        # Create a new commit on main
        with open("another.txt", "w") as f:
            f.write("Another main commit")
        run_command(["git", "add", "another.txt"])
        run_command(["git", "commit", "-m", "Another commit on main"])

        # Create a branch from the old commit
        run_command(["git", "checkout", "HEAD~1"])  # go back one commit
        run_command(["git", "checkout", "-b", "feature-rebase"])
        with open("rebase.txt", "w") as f:
            f.write("Rebase content")
        run_command(["git", "add", "rebase.txt"])
        run_command(["git", "commit", "-m", "Rebase commit"])

        # Now go to main and rebase that branch onto main
        run_command(["git", "checkout", "main"])
        # Fast-forward rebase is effectively a cherry-pick, but let's do an actual rebase:
        # We'll do 'git merge-base' check to ensure they're not linear, but let's do normal rebase
        run_command(["git", "rebase", "feature-rebase"], cwd=self.test_dir)
        # Because we have a simple scenario, this might end up with a fast-forward or a single rebase commit.

        # Run the "list" command
        cmd = ["python3", SCRIPT_PATH, "list", "main"]
        stdout, _ = run_command(cmd)
        # We expect 'feature-rebase' => rebased (since there's no merge commit)
        self.assertIn("feature-rebase => rebased", stdout)

    def test_delete_commands(self):
        """
        Test deleting branches by classification.
        """
        # Create 'identical' branch
        run_command(["git", "checkout", "-b", "identical-branch"])
        run_command(["git", "checkout", "main"])

        # Create 'merged' branch
        run_command(["git", "checkout", "-b", "merged-branch"])
        with open("merged.txt", "w") as f:
            f.write("merged content")
        run_command(["git", "add", "merged.txt"])
        run_command(["git", "commit", "-m", "Add merged content"])
        run_command(["git", "checkout", "main"])
        run_command(["git", "merge", "merged-branch", "--no-edit"])

        # Create 'rebased' branch
        run_command(["git", "checkout", "HEAD~1"])  # back one commit
        run_command(["git", "checkout", "-b", "rebased-branch"])
        with open("rebased.txt", "w") as f:
            f.write("rebased content")
        run_command(["git", "add", "rebased.txt"])
        run_command(["git", "commit", "-m", "Add rebased content"])
        run_command(["git", "checkout", "main"])
        run_command(["git", "rebase", "rebased-branch"])

        # Now delete branches by classification
        # 1) identical
        run_command(["python3", SCRIPT_PATH, "delete-identical", "main"])
        stdout, _ = run_command(["git", "branch", "--list"])
        self.assertNotIn("identical-branch", stdout)

        # 2) merged
        run_command(["python3", SCRIPT_PATH, "delete-merged", "main"])
        stdout, _ = run_command(["git", "branch", "--list"])
        self.assertNotIn("merged-branch", stdout)

        # 3) rebased
        run_command(["python3", SCRIPT_PATH, "delete-rebased", "main"])
        stdout, _ = run_command(["git", "branch", "--list"])
        self.assertNotIn("rebased-branch", stdout)


if __name__ == "__main__":
    unittest.main()