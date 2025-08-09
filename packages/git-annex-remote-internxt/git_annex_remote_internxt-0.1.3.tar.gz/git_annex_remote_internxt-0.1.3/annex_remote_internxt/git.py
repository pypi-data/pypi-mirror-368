import os
import subprocess
from pathlib import Path


def _call_git(
    args: list[str],
    *,
    capture_output: bool = False,
    cwd: Path | None = None,
    check: bool = False,
    text: bool | None = None,
    inputs: str | bytes | None = None,
    force_c_locale: bool = False,
) -> subprocess.CompletedProcess:
    """Wrapper around ``subprocess.run`` for calling Git

    ``args`` is a list of argument for the Git command. This list must not
    contain the Git executable itself. It will be prepended (unconditionally)
    to the arguments before passing them on.

    If ``force_c_locale`` is ``True`` the environment of the Git process
    is altered to ensure output according to the C locale. This is useful
    when output has to be processed in a locale invariant fashion.

    All other argument are pass on to ``subprocess.run()`` verbatim.
    """
    env = None
    if force_c_locale:
        env = dict(os.environ, LC_ALL='C')

    # make configurable
    git_executable = 'git'
    cmd = [git_executable, *args]
    return subprocess.run(
        cmd,
        capture_output=capture_output,
        cwd=cwd,
        check=check,
        text=text,
        input=inputs,
        env=env,
    )


def call_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    force_c_locale: bool = False,
    text: bool | None = None,
    capture_output: bool = False,
) -> str | bytes | None:
    """Call Git with no output capture, raises on non-zero exit.

    If ``cwd`` is not None, the function changes the working directory to
    ``cwd`` before executing the command.

    If ``force_c_locale`` is ``True`` the environment of the Git process
    is altered to ensure output according to the C locale. This is useful
    when output has to be processed in a locale invariant fashion.

    If ``capture_output`` is ``True``, process output is captured (and not
    relayed to the parent process/terminal). This is necessary for reporting
    any error messaging via a ``CommandError`` exception.  By default process
    output is not captured.

    All other argument are pass on to ``subprocess.run()`` verbatim.

    If ``capture_output`` is enabled, the captured STDOUT is returned as
    ``str`` or ``bytes``, depending on the value of ``text``. Otherwise
    ``None`` is returned to indicate that no output was captured.
    """
    res = _call_git(
        args,
        capture_output=capture_output,
        cwd=cwd,
        check=True,
        text=text,
        force_c_locale=force_c_locale,
    )
    return res.stdout if capture_output else None
