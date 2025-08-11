import uuid
from pathlib import PurePosixPath

import pytest

from annex_remote_internxt.internxt_drive import (
    DriveFSError,
    InternxtDrive,
    InternxtError,
)


def test_drive_instance():
    # should always work, doesn't interact with internxt until
    # the first real operation
    InternxtDrive()


def test_drive_create_folder(internxt, internxt_drive):  # noqa ARG001
    drv = internxt_drive
    # we cannot create the root folder
    with pytest.raises(DriveFSError, match='Cannot create root'):
        drv.create_folder(PurePosixPath())
    # but we can tolerate the attempt if told
    drv.create_folder(PurePosixPath(), exists_ok=True)

    path = PurePosixPath('test_drive_create_folder')
    drv.create_folder(path)
    # cannot blindly recreate in the same place, by default
    with pytest.raises(DriveFSError, match='already exists'):
        drv.create_folder(path)
    # but on demand it can
    drv.create_folder(path, exists_ok=True)
    assert drv.folder_exists(path)
    # we cannot create a folder with missing parents, by default
    deep_path = PurePosixPath(path, 'sub', 'target')
    with pytest.raises(DriveFSError, match='Parent.*does not exist'):
        drv.create_folder(deep_path)
    # but on demand we can
    drv.create_folder(deep_path, parents=True)
    assert drv.folder_exists(deep_path)

    # place some delete tests here for procedural efficiency
    # will not delete non-empty folder, by default
    with pytest.raises(DriveFSError, match='not empty'):
        drv.deleted_folder_permanently(deep_path.parent)
    # but can if instructed
    drv.deleted_folder_permanently(deep_path.parent, empty_only=False)
    assert not drv.folder_exists(deep_path)
    assert not drv.folder_exists(deep_path.parent)


def test_drive_invalid_root_id(internxt):  # noqa ARG001
    # can detect that a given root folder does not exist
    assert not InternxtDrive(uuid.uuid4()).folder_exists(PurePosixPath())
    path = PurePosixPath('dummy')
    # wrong kind of root folder id
    with pytest.raises(InternxtError, match='must be a valid v4'):
        InternxtDrive(uuid.uuid1()).create_folder(path)
    # root folder id with no matching folder
    with pytest.raises(InternxtError, match='does not exist'):
        InternxtDrive(uuid.uuid4()).create_folder(path)


def test_drive_folder_exists(internxt, internxt_drive):  # noqa ARG001
    path = PurePosixPath('test_drive_folder_exists')
    drv = internxt_drive
    # can detect that a given root folder does exist
    assert drv.folder_exists(PurePosixPath())
    assert not drv.folder_exists(path)
    drv.create_folder(path)
    assert drv.folder_exists(path)


def test_drive_file_exists(internxt, internxt_drive):  # noqa ARG001
    fpath = PurePosixPath('test_drive_file_exists')
    drv = internxt_drive
    assert not drv.file_exists(fpath)
    # check code path where a missing parent folder provides
    # the evidence for a non-existing file
    assert not drv.file_exists(fpath / 'dummy')
    # create a folder in that place
    drv.create_folder(fpath)
    # it is not mistaken for a file
    assert not drv.file_exists(fpath)


def test_drive_no_delete_root(internxt, internxt_drive):  # noqa ARG001
    with pytest.raises(
        DriveFSError,
        match='Deleting the root folder is not supported',
    ):
        internxt_drive.deleted_folder_permanently(PurePosixPath())


def test_drive_fileio(internxt, internxt_drive, tmp_path):  # noqa ARG001
    drv = internxt_drive
    path = PurePosixPath('test_drive_fileio')
    drv.create_folder(path)

    test_fpath = tmp_path / 'dummy.txt'
    # internxt does not support empty files
    test_fpath.write_text('some text')
    drv.upload(test_fpath, path)
    assert drv.file_exists(path / test_fpath.name)
    # upload again to the same location with different content
    test_fpath.write_text('other text')
    drv.upload(test_fpath, path)
    assert drv.file_exists(path / test_fpath.name)

    download_dir = tmp_path / 'download'
    download_dir.mkdir()
    drv.download(path / test_fpath.name, download_dir)
    assert (download_dir / test_fpath.name).read_text() == test_fpath.read_text()


def test_drive_download_error(internxt, internxt_drive, tmp_path):  # noqa ARG001
    with pytest.raises(DriveFSError, match='does not exist'):
        internxt_drive.download(
            PurePosixPath('test_drive_dowload_error'),
            tmp_path,
        )
