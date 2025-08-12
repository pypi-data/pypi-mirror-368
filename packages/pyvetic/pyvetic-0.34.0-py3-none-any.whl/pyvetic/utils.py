import os
import subprocess


def get_repo_name():
    try:
        # Get the top-level directory of the git repo
        repo_path = (
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )

        # Repo name is the name of the top-level directory
        return os.path.basename(repo_path)
    except Exception:
        return None
