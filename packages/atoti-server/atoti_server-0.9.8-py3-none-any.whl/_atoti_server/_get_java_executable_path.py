import os
import re
from functools import cache
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output


def _extract_java_version(java_version_output: str, /) -> int:
    for _line in java_version_output.splitlines():
        line = _line.strip()
        match = re.match(r"^java\.specification\.version\s?=\s?(?P<version>\d+)$", line)

        if not match:
            continue

        version = match.group("version")
        if not version:
            raise ValueError(f"Cannot find Java version in `{line}`.")

        return int(version)

    raise RuntimeError(f"Failed to extract Java version from\n{java_version_output}")


@cache
def _get_java_version(java_home: Path, /) -> int:
    java_executable_path = java_home / "bin" / "java"

    try:
        output = check_output(  # noqa: S603
            [
                java_executable_path,
                "-XshowSettings:properties",  # spell-checker: disable-line
                "-version",
            ],
            stderr=STDOUT,
            text=True,
        )
    except CalledProcessError as error:
        raise RuntimeError(f"Cannot retrieve Java version:\n{error.output}") from error

    return _extract_java_version(output)


def _get_java_home(*, supported_java_version: int) -> Path:
    java_home = os.environ.get("JAVA_HOME")

    if java_home and (_get_java_version(Path(java_home)) == supported_java_version):
        return Path(java_home)

    # Importing jdk4py lazily to let the previous branch a chance to run in environments where jdk4py is not installed.
    from jdk4py import (  # pylint:disable=nested-import,undeclared-dependency
        JAVA_HOME,
        JAVA_VERSION,
    )

    if JAVA_VERSION[0] != supported_java_version:
        raise RuntimeError(f"No installation of Java {supported_java_version} found.")

    return JAVA_HOME


def get_java_executable_path(
    *,
    executable_name: str = "java",
    supported_java_version: int,
) -> Path:
    java_home = _get_java_home(supported_java_version=supported_java_version)
    return java_home / "bin" / executable_name
