"""Helpers to call the internxt CLI."""
# This module shall not contain (convenience) implementations on top of the
# CLI. See `internxt_drive` for that.

import base64
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import UUID


class InternxtError(RuntimeError):
    """Exception raised on unsuccessful Internxt API calls"""


def call_internxt(
    cmd: str,
    *,
    args: list[str] | None = None,
) -> dict[str, Any]:
    """Call the internxt CLI

    Any internxt CLI command is executed in non-interactive mode,
    and with JSON-formatted result output.

    On any error, a ``InternxtError`` exception is raised,
    with the error message produced by the CLI.

    The CLI command output is returned unmodified in deserialized
    form as a dictionary.
    """
    dbg_id = None
    if 'INTERNXT_DEBUG' in os.environ:
        # have a short random identifier that can be used to
        # connect start and finish message.
        # this is not really "unique", just good enough
        dbg_id = base64.b64encode(os.urandom(32))[:4].decode('ascii')
        print(f'INXT[{dbg_id}] RUN {cmd}({args!r})', file=sys.stderr)  # noqa: T201
    try:
        cp = subprocess.run(
            ['internxt', cmd, '-x', '--json', *(args or [])],  # noqa: S607
            capture_output=True,
            # TODO: timeout,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        # this could be an ordinary exit with a JSON error message
        msg = ''
        try:
            res = json.loads(e.stdout)
            msg = res['message']
        except Exception:  # noqa BLE001
            # we could not extract a message, let's reraise
            # the original exception
            raise e from None
        if dbg_id:
            print(  # noqa: T201
                f'INXT[{dbg_id}] ERROR {res!r} '
                f'[CODE={e.returncode}, STDERR={e.stderr!r}',
                file=sys.stderr,
            )
        raise InternxtError(msg) from e
    else:
        if dbg_id:
            print(f'INXT[{dbg_id}] OK', file=sys.stderr)  # noqa: T201

    try:
        res = json.loads(cp.stdout)
    except Exception as e:
        msg = 'malformed API response'
        if dbg_id:
            print(f'INXT[{dbg_id}] ERROR {msg}: {e}', file=sys.stderr)  # noqa: T201
        raise InternxtError(msg) from e

    # if the API always exists non-zero on a success=False result,
    # we will never hit this conditional
    if not res['success']:
        # the API communicates that the command did not work.
        # it typically carries a message explaining the failure
        msg = res.get('message')
        if dbg_id:
            print(f'INXT[{dbg_id}] ERROR {msg}', file=sys.stderr)  # noqa: T201
        raise InternxtError(msg)

    # TODO: the top-level keys pf `res` might also contain
    # a `message` that could be communicated in some standard
    # fashion somehow
    return res


def internxt_whoami() -> dict[str, Any]:
    """List relevant information about the user logged into the Internxt CLI"""
    return call_internxt('whoami')


def internxt_config() -> dict[str, Any]:
    """Display limited information about the logged in user, including available
    space, used space and root folder ID"""
    return call_internxt('config')


def internxt_list(
    folder_id: UUID | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """List the content of an internxt drive folder

    The folder to list must be identified by its folder UUID. If
    not UUID is given, the root folder will be listed.

    Returns a dictionary with two keys: 'folders' and 'files'.
    """
    res = call_internxt('list', args=[f'--id={folder_id or ""}'])
    # main results is 'folders' and 'files' under 'list'
    return res['list']


def internxt_create_folder(
    name: str,
    parent_folder_id: UUID | None = None,
) -> dict[str, Any]:
    """
    Returns a dictionary with the properties of the created folder.
    """
    res = call_internxt(
        'create-folder',
        args=[
            f'--id={parent_folder_id or ""}',
            f'--name={name}',
        ],
    )
    return res['folder']


def internxt_delete_permanently_folder(
    folder_id: UUID | None,
) -> None:
    """ """
    call_internxt(
        'delete-permanently-folder',
        args=[f'--id={folder_id or ""}'],
    )


def internxt_delete_permanently_file(
    file_id: UUID | None,
) -> None:
    """ """
    call_internxt(
        'delete-permanently-file',
        args=[f'--id={file_id or ""}'],
    )


def internxt_upload_file(
    src: Path,
    parent_folder_id: UUID | None = None,
) -> dict[str, Any]:
    """
    The file name of ``src`` is also the target file name
    in the destination folder.
    """
    res = call_internxt(
        'upload-file',
        args=[
            f'--destination={parent_folder_id or ""}',
            f'--file={src}',
        ],
    )
    return res['file']


def internxt_download_file(
    file_id: UUID | None,
    dest_dir: Path,
) -> dict[str, Any]:
    """
    The file name of ``src`` is also the target file name
    in the destination directory.

    Any conflicting file in the destination directory is overwritten.
    """
    res = call_internxt(
        'download-file',
        args=[
            f'--directory={dest_dir}',
            f'--id={file_id or ""}',
            '--overwrite',
        ],
    )
    return res['file']


def internxt_move_file(
    file_id: UUID,
    parent_folder_id: UUID | None = None,
) -> dict[str, Any]:
    """ """
    res = call_internxt(
        'move-file',
        args=[
            f'--destination={parent_folder_id or ""}',
            f'--id={file_id}',
        ],
    )
    # main results is 'folders' and 'files' under 'list'
    return res['file']
