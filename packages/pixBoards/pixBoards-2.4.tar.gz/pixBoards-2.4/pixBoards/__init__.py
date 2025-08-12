import subprocess


def get_git_version():
    try:
        commit_hash = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode()
            .strip()
        )
        return commit_hash
    except Exception:
        return "untracked"


__version__ = get_git_version()
