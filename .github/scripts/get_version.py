import datetime
import subprocess
import sys


def get_current_version() -> str:
    # get the latest tag
    tag = subprocess.check_output(
        ["git", "describe", "--abbrev=0", "--tags"], text=True
    ).strip()
    version = tag.lstrip("v")
    return version


def get_next_version(patch: bool = False) -> str:
    current_version = get_current_version()
    version_parts = current_version.split(".")
    if len(version_parts) != 3:
        version_parts.append("0")
    if patch:
        version_parts[2] = str(int(version_parts[2]) + 1)
        return ".".join(version_parts)
    else:
        major, minor, _ = version_parts
        this_year = str(datetime.datetime.now(tz=datetime.UTC).year)[-2:]
        if this_year == major:
            minor = str(int(minor) + 1)
        else:
            major = this_year
            minor = "0"
        return f"{major}.{minor}"


if __name__ == "__main__":
    patch = "--patch" in sys.argv or "-p" in sys.argv
    print(get_next_version(patch))
