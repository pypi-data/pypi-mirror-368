import logging
import os
import subprocess
import sys

from git import Repo

logger = logging.getLogger("bfjira")


def to_git_root():
    try:
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], universal_newlines=True
        ).strip()
        os.chdir(git_root)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to find git repository root: {e}")
        sys.exit(1)


def stash_changes():
    """Stash uncommitted changes."""
    try:
        repo = Repo(".")
        repo.git.stash("push", "-u", "-m", "bfjira auto-stash")  # -u includes untracked
        logger.info("Stashed uncommitted changes.")
        return True
    except Exception as e:
        logger.error(f"Failed to stash changes: {e}")
        return False


def pop_stash():
    """Pop the latest stash."""
    try:
        repo = Repo(".")
        repo.git.stash("pop")
        logger.info("Popped stashed changes.")
    except Exception as e:
        # Common issue: conflicts after pop. Log and inform, but don't crash.
        logger.warning(f"Failed to pop stash cleanly: {e}")
        logger.warning("You may need to resolve conflicts manually ('git status').")


def create_branch(branch_name, set_upstream=True):
    """
    Create a new Git branch and optionally set upstream.
    Assumes repository is clean or changes have been stashed.
    """
    try:
        repo = Repo(".")
        origin = repo.remotes.origin
        origin.pull()
        logger.info("Pulled the latest changes from the remote repository.")

        repo.create_head(branch_name).checkout()
        logger.info(f"Created and checked out new branch '{branch_name}'.")

        if set_upstream:
            origin.push(branch_name, set_upstream=True)
            logger.info(f"Pushed '{branch_name}' and set upstream.")
    except Exception as e:
        logger.error(f"Error while creating Git branch '{branch_name}': {e}")
        raise
