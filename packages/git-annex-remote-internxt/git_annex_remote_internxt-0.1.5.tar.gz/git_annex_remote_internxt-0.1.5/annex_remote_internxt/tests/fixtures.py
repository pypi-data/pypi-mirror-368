import platform
from collections.abc import Generator
from datetime import (
    datetime,
    timezone,
)
from pathlib import (
    Path,
    PurePosixPath,
)
from shutil import which

import pytest

from annex_remote_internxt.git import (
    call_git,
)
from annex_remote_internxt.internxt_cli import (
    call_internxt,
    internxt_create_folder,
    internxt_delete_permanently_folder,
)
from annex_remote_internxt.internxt_drive import (
    InternxtDrive,
)


@pytest.fixture(autouse=True, scope='session')
def internxt_binary() -> str | None:
    """Is the internxt CLI installed?"""
    return which('internxt')


# TODO: return UUID
@pytest.fixture(autouse=False, scope='session')
def internxt_root_uuid(internxt_binary) -> str | None:
    """"""
    if not internxt_binary:
        return None
    res = call_internxt('whoami')
    if not res['success']:
        return None
    return res['login']['user']['rootFolderId']


# TODO: return UUID
@pytest.fixture(autouse=False, scope='session')
def internxt_testroot_uuid(internxt_root_uuid) -> Generator[str | None]:
    """"""
    if not internxt_root_uuid:
        yield None
        return
    test_root_path = (
        'pytest-annexremote-'
        f'{platform.node()}-'
        f'{datetime.now(tz=timezone.utc).isoformat()}'
    )

    test_root_props = internxt_create_folder(test_root_path)
    test_root_uuid = test_root_props['uuid']

    yield test_root_uuid

    internxt_delete_permanently_folder(test_root_uuid)


@pytest.fixture(autouse=False, scope='session')
def internxt_drive(internxt_testroot_uuid) -> InternxtDrive:
    """Session-wide `InternxtDrive` instance for the `test_root_uuid`"""
    return InternxtDrive(internxt_testroot_uuid)


@pytest.fixture(autouse=False, scope='function')  # noqa: PT003
def internxt(internxt_testroot_uuid) -> str | None:
    if not internxt_testroot_uuid:
        pytest.skip('No usable internxt CLI found.')
    return internxt_testroot_uuid


@pytest.fixture(autouse=False, scope='function')  # noqa: PT003
def gitrepo(tmp_path_factory) -> Generator[Path]:
    """Yield the path to an initialized Git repository"""
    # must use the factory to get a unique path even when a concrete
    # test also uses `tmp_path`
    path = tmp_path_factory.mktemp('gitrepo')
    call_git(
        ['init'],
        cwd=path,
        capture_output=True,
    )
    return path


@pytest.fixture(autouse=False, scope='function')  # noqa: PT003
def annexrepo(gitrepo) -> Generator[Path]:
    """Yield the path to a Git repository with an initialized annex"""
    call_git(
        ['annex', 'init'],
        cwd=gitrepo,
        capture_output=True,
    )
    return gitrepo


@pytest.fixture(autouse=False, scope='function')  # noqa: PT003
def populated_annexrepo(annexrepo) -> Generator[Path]:
    """Yield the path to a git-annex repo with a few files"""
    repocontent = (
        ('file1.txt', 'content of file1.txt'),
        ('file2.csv', 'content of file2.csv'),
        ('subdir/file1.txt', 'content of subdir/file1.txt'),
        ('subdir/subsubdir/file2.csv', 'content of subdir/subsubdir/file2.csv'),
    )

    for file, content in repocontent:
        fpath = annexrepo / (PurePosixPath(file))
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content)
    call_git(
        ['annex', 'add', '.'],
        cwd=annexrepo,
        capture_output=True,
    )
    call_git(['commit', '-m', 'payload'], cwd=annexrepo, capture_output=True)
    return annexrepo
