import subprocess

def test_identical_branches():
    subprocess.run(["git", "checkout", "-b", "test-branch"], check=True)
    output = subprocess.run(["git", "identical-branches"], capture_output=True, text=True)
    assert "test-branch" in output.stdout

def test_merged_branches():
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "merge", "test-branch"], check=True)
    output = subprocess.run(["git", "identical-branches", "--merged"], capture_output=True, text=True)
    assert "test-branch" in output.stdout

if __name__ == "__main__":
    test_identical_branches()
    test_merged_branches()
    print("All tests passed!")