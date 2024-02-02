import datetime
import subprocess


def get_current_version() -> str:
    # get the latest tag
    tag = subprocess.check_output(["git", "describe", "--abbrev=0"], text=True).strip()
    version = tag.lstrip("v")
    return version


def get_next_version() -> str:
    current_version = get_current_version()
    major, minor = current_version.split(".")[:2]
    this_year = str(datetime.datetime.now(tz=datetime.UTC).year)[-2:]
    if this_year == major:
        minor = str(int(minor) + 1)
    else:
        major = this_year
        minor = "0"
    return f"{major}.{minor}"


if __name__ == "__main__":
    print(get_next_version())
