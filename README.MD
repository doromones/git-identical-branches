# git-identical-branches

A Git extension to find and manage local branches that have no changes relative to a specified branch (by default, the current `HEAD`).

## Features

- Lists local branches that are:
    - **identical** (same commit SHA)
    - **merged** (fully contained via a merge commit)
    - **rebased** (fully contained without a merge commit)
- Deletes branches by classification:
    - `delete-identical`
    - `delete-merged`
    - `delete-rebased`

## Usage

```bash
git identical-branches <subcommand> [reference]

```

## Help

```bash
git identical-branches --help

usage: git-identical-branches [-h] {list,delete-merged,delete-rebased,delete-identical} ...

git-identical-branches: A Git extension to find and manage local branches that have no changes relative to a specified branch (by default, HEAD).

positional arguments:
  {list,delete-merged,delete-rebased,delete-identical}
    list                List local branches that are fully contained in the reference (with classification).
    delete-merged       Delete local branches that were integrated via a merge commit.
    delete-rebased      Delete local branches that were integrated without a merge commit (rebase/fast-forward).
    delete-identical    Delete local branches that are identical (same SHA) to the reference.

optional arguments:
  -h, --help            show this help message and exit
```

## Install

### Curl
```bash
sudo curl -L "https://raw.githubusercontent.com/doromones/git-identical-branches/main/git-identical-branches.py" \
     -o /usr/local/bin/git-identical-branches
sudo chmod +x /usr/local/bin/git-identical-branches
```

### Local
```bash
./install.sh
```

```bash
Copying to /usr/local/bin/git-identical-branches (sudo may prompt for password)...
Making git-identical-branches.py executable...
Installation complete. You can now use 'git identical-branches <subcommand>' or call it directly:
  git-identical-branches <subcommand>
```