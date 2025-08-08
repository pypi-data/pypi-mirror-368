"""Setup file for package."""

from pathlib import Path
from subprocess import CalledProcessError, run

from setuptools import find_packages, setup

git_root_path = (Path(__file__).parent / "../..").resolve()


def get_version():
    """We want the semantic version to come in the form of `git describe`.

    Our naming scheme is at odds with PEP 440, so we have to
    make it conforming but using "+" to join the public
    identity (version.txt) with our local identifier, which
    is the string that git describe appends.
    """

    with open(git_root_path / "version.txt", encoding="utf-8") as f:
        version_txt = f.read().strip()
    try:
        semver = run(
            [git_root_path / "ci/bin/rime-semver"],
            check=True,
            encoding="utf-8",
            capture_output=True,
        ).stdout.strip()
    except (CalledProcessError, AttributeError):
        semver = version_txt

    return semver


setup(
    version=get_version(),
    packages=find_packages(include=["rime_sdk*"]),
)
