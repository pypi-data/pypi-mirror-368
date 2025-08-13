from datetime import timedelta
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output

from ._get_java_executable_path import get_java_executable_path
from ._supported_java_version import SUPPORTED_JAVA_VERSION


def _get_jfr_command(jfr_action: str, /, *args: str, pid: int) -> list[Path | str]:
    return [
        get_java_executable_path(
            executable_name="jcmd",
            supported_java_version=SUPPORTED_JAVA_VERSION,
        ),
        str(pid),
        f"JFR.{jfr_action}",
        *args,
    ]


def create_flight_recording(path: Path, /, *, duration: timedelta, pid: int) -> None:
    """Create a recording file using Java Flight Recorder (JFR).

    This call is non-blocking: ``jcmd`` will continue writing to the file at the specified *path* for the given *duration* after this function returns.
    Call :func:`time.sleep` with ``duration.total_seconds()`` to block the current thread until the end of the recording.

    Args:
        path: The path (with a :guilabel:`.jfr` extension) at which the recording file should be written to.
        duration: The duration of the recording.
        pid: The process ID of the Java process to record.
    """
    command = _get_jfr_command(
        "start",
        f"duration={int(duration.total_seconds())}s",
        f"filename={path}",
        pid=pid,
    )

    try:
        check_output(  # noqa: S603
            command,
            stderr=STDOUT,
            text=True,
        )
    except CalledProcessError as error:
        raise RuntimeError(
            f"Failed to create flight recording:\n{error.output}",
        ) from error
