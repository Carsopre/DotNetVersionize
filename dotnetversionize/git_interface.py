import subprocess


def get_latest_tag() -> str:
    # Get latest tag
    _command = "git fetch --tags"
    subprocess.run(_command.split())
    _command = "git tag --sort=committerdate -l"
    _result = subprocess.run(_command.split(), capture_output=True, text=True)
    assert _result.returncode == 0

    _tags = _result.stdout.strip().split("\n")
    if not _tags:
        print("No git tags found, bumping cancelled.")
        exit(code=1)
    return _tags[-1]


def get_commit_list(git_range: str) -> list[str]:
    _command = f"git log {git_range} --pretty=format:%s"
    # _command = f"git log {git_range} --format=%B"
    _result = subprocess.run(_command.split(), capture_output=True, text=True)
    assert _result.returncode == 0

    _commits = list(filter(lambda x: x.strip(), _result.stdout.strip().split("\n")))
    if not _commits:
        print("No commits found, bumping cancelled.")
        exit(code=1)

    return _commits
