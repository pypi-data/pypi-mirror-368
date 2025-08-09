import json
import logging
import tempfile
from pathlib import (
    Path,
    PurePosixPath,
)
from typing import (
    TYPE_CHECKING,
    Any,
)
from uuid import UUID

from annexremote import (
    ExportRemote,
    Master,
    RemoteError,
    UnsupportedRequest,
)

import annex_remote_internxt.internxt_cli as cli
from annex_remote_internxt.internxt_drive import (
    DriveFSError,
    InternxtDrive,
    InternxtError,
    _Unset,
)


class AnnexRemoteInternxt(ExportRemote):
    drive_config_fname = '.internxt_annexremote.json'
    # a dict in practice, but declared here in immutable form
    drive_default_config = (('layout', 1),)

    def __init__(self, annex: Master) -> None:
        super().__init__(annex)
        self.configs = {
            'folder': 'UUID or relative path of the directory on internxt. '
            "A UUID needs to be prefixed with 'uuid:'",
        }
        self._info: dict[str, Any] | type[_Unset] = _Unset
        self._folder_id: UUID | None | type[_Unset] = _Unset
        self._drive: InternxtDrive | None = None
        self._drive_config: dict[str, Any] | None = None
        self._gitdir: Path | None = None

    @property
    def gitdir(self) -> Path:
        if self._gitdir is None:
            self._gitdir = Path(self.annex.getgitdir())
        return self._gitdir

    @property
    def info(self) -> dict[str, Any]:
        if self._info is _Unset:
            self._info = {
                'folder_id': self.folder_id,
                'folder': self.annex.getconfig('folder'),
            }
        if TYPE_CHECKING:
            assert not isinstance(self._info, type)
        return self._info

    @info.setter
    def info(self, value: dict[str, Any]) -> None:
        self._info = value

    @property
    def folder_id(self) -> UUID | None:
        """Lazy property for the internxt folder UUID

        This getter performs resolution of drive paths as
        necessary to determine a UUID.

        The main input is the "folder" remote configuration item.

        Raises `ValueError` when a configured path is not
        found in the drive.
        """
        if self._folder_id is not _Unset:
            if TYPE_CHECKING:
                assert not isinstance(self._folder_id, type)
            return self._folder_id

        # code below only runs once in the lifetime of a remote
        # instance
        user = ensure_login()
        self.annex.debug(f'Logged in as user {user}.')

        match self.annex.getconfig('folder'):
            case None:
                msg = 'You need to set folder='
                raise RemoteError(msg)
            case 'uuid:':
                # the drive's root folder
                self._folder_id = None
            case s if s.startswith('uuid:'):
                self._folder_id = UUID(s[5:])
            case _ as path:
                self._folder_id = InternxtDrive().get_folder_id(PurePosixPath(path))

        return self._folder_id

    @property
    def drive(self) -> InternxtDrive:
        if self._drive is None:
            self._drive = InternxtDrive(self.folder_id)
        return self._drive

    @property
    def drive_config(self) -> dict[str, Any]:
        """Configuration of the remote deposit on the drive

        An empty record is return when no configuration is
        found or when the deposit on the drive doesn't exist
        at all.
        """
        if self._drive_config is None:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                cfg_name = AnnexRemoteInternxt.drive_config_fname
                try:
                    self.drive.download(PurePosixPath(cfg_name), tmp_path)
                except DriveFSError:
                    # could not download, because the file is not
                    # around. we know, because it is not
                    # a generic InternxtError
                    self._drive_config = {}
                else:
                    with (tmp_path / cfg_name).open() as f:
                        self._drive_config = json.load(f)
        return self._drive_config

    def initremote(self) -> None:
        # TODO: place a layout marker on the drive folder.
        # good chance that we might regret the current placement choices
        try:
            self.folder_id  # noqa: B018
        except DriveFSError:
            # we get here when `folder` was configured with a drive
            # folder path and that folder does not exist.
            self.annex.debug('internxt drive target folder does not yet exist')
            # so create it...
            path = PurePosixPath(self.annex.getconfig('folder'))
            InternxtDrive().create_folder(
                path,
                parents=True,
            )
        if not self.drive_config:
            # the remote location does not have a configuration.
            # drop the current standard in
            with tempfile.TemporaryDirectory() as tmpdir:
                fpath = Path(tmpdir) / AnnexRemoteInternxt.drive_config_fname
                fpath.write_text(
                    json.dumps(
                        dict(AnnexRemoteInternxt.drive_default_config),
                    )
                )
                try:
                    self.drive.upload(
                        fpath,
                        # upload into the root
                        PurePosixPath(),
                    )
                except InternxtError as e:
                    # we cannot deposit the config. this may well be
                    # because the folder uuid is invalid (e.g. deleted
                    # node in the meantime)
                    msg = (
                        'Cannot place configuration on drive. '
                        'Invalid folder configuration '
                        f"'{self.annex.getconfig('folder')}'? "
                        f'[{e!r}]'
                    )
                    raise RemoteError(msg) from e

                # avoid download roundtrip
                self._drive_config = dict(AnnexRemoteInternxt.drive_default_config)

    def prepare(self) -> None:
        # dummy run that triggers the ID resolution for now.
        # TODO: must (later) check if that folder actually exists.
        # but this may better be done when trying to do something
        # with that folder, rather than an (expensive) upfront check
        # self.folder_id
        pass

    def _get_key_path(self, key: str) -> PurePosixPath:
        # switch based on drive layout marker
        layout = self.drive_config['layout']
        match layout:
            case 1:
                # we use also a dirhash directory tree, because of this
                # report https://github.com/internxt/cli/issues/321
                # (too many items in a dir bring the API down)
                key_path = PurePosixPath(
                    self.annex.dirhash_lower(key),
                    key,
                )
            case _:
                msg = f'Unsupported drive layout version {layout!r}'
                raise RemoteError(msg)
        return key_path

    def _checkpresent(self, remote_path: PurePosixPath) -> bool:
        # TODO: wrap in try-except to raise RemoteError
        # raise RemoteError if the presence of the key couldn't be
        # determined, eg. in case of connection error
        return self.drive.file_exists(remote_path)

    def checkpresent(self, key: str) -> bool:
        # we cannot just check if we know a file UUID
        # file_uuid = self.annex.getstate(key)
        # return file_uuid != ''
        # this would treat the local knowledge as unconditionally valid,
        # but this method is the one used to verfit the state of the
        # remote
        return self._checkpresent(self._get_key_path(key))

    def checkpresentexport(
        self,
        key: str,  # noqa: ARG002
        remote_file: str,
    ) -> bool:
        return self._checkpresent(PurePosixPath(remote_file))

    def _store(
        self,
        key: str,  # noqa: ARG002
        local_path: Path,
        remote_path: PurePosixPath,
    ) -> UUID:
        # store the file in `filename` to a unique location derived from `key`
        # raise RemoteError if the file couldn't be stored

        if remote_path.name != local_path.name:
            msg = (
                'Rename prior upload is not implemented yet: '
                f'{local_path} -> {remote_path}'
            )
            raise RemoteError(msg)
        # avoid testing presence of root folder again
        if remote_path.parent != PurePosixPath():
            self.drive.create_folder(
                remote_path.parent,
                parents=True,
                exists_ok=True,
            )
        return self.drive.upload(local_path, remote_path.parent)

    def transfer_store(self, key: str, filename: str) -> None:
        # store the file in `filename` to a unique location derived from `key`
        # raise RemoteError if the file couldn't be stored
        fuuid = self._store(
            key,
            Path(filename),
            self._get_key_path(key),
        )
        # we register the file node UUID to enable one-request downloads
        # and also robustify against reorganizations on the drive.
        # this can only be done for non-export mode, otherwise
        # an fsck would succeed for any file exported from the same key,
        # even if that particular duplicate is no longer on the remote.
        self.annex.setstate(key, str(fuuid))

    def transferexport_store(
        self,
        key: str,
        local_file: str,
        remote_file: str,
    ) -> None:
        # we cannot rename files on the drive after upload without
        # limitations. we need to rename locally, because the source file
        # is a key file, and the destination is not.
        # on sensible platforms the cheapest is a hardlink.
        # we should not copy (expensive), and we do not
        # know if the source file can be renamed directly without issues.
        # os.link() works on unix/win, we just need to deal with
        # the situation that we cannot place a hardlink next to the source
        # file
        with tempfile.TemporaryDirectory(
            dir=self.gitdir / 'annex',
        ) as tmpdir:
            local_file_path = Path(local_file)
            remote_file_path = PurePosixPath(remote_file)
            upload_path = Path(tmpdir) / remote_file_path.name
            upload_path.hardlink_to(local_file_path)
            self._store(
                key,
                upload_path,
                remote_file_path,
            )

    def _retrieve(
        self,
        key: str,
        remote_path: PurePosixPath,
        dest_path: Path,
    ) -> None:
        # raise RemoteError if the file couldn't be retrieved
        if dest_path.exists():
            # the CLI download does not support resuming
            # downloads, but git-annex placed the content
            # of interrupted attempts at `filename`
            dest_path.unlink()

        dest_dir = dest_path.parent
        if remote_path.name != dest_path.name:
            # we need to rename the file after download.
            # best way is to have a download dir underneath
            # `self.gitdir / annex / tmp` and then move to
            # `dest_path`
            # if `filename` is already in the tmp dir
            # (which it commonly (always?) is, we can do the
            # rename right there
            tmp_dest_path = dest_dir / remote_path.name
            if (
                not (
                    Path('.git', 'annex', 'tmp') in tmp_dest_path.parents
                    or Path('.git', 'annex', 'othertmp') in tmp_dest_path.parents
                )
                and tmp_dest_path.exists()
            ):
                msg = f'Conflicting content at download target {tmp_dest_path}'
                raise RemoteError(msg)

        fuuid = self.annex.getstate(key)
        if fuuid:
            cli.internxt_download_file(UUID(fuuid), dest_dir)
        else:
            # we have no file node UUID on record, download
            # via the key path
            self.drive.download(remote_path, dest_dir)
        if remote_path.name != dest_path.name:
            tmp_dest_path.rename(dest_path)

    def transfer_retrieve(self, key: str, filename: str):
        # get the file identified by `key` and store it to `filename`
        # raise RemoteError if the file couldn't be retrieved
        self._retrieve(
            key,
            self._get_key_path(key),
            Path(filename),
        )

    def transferexport_retrieve(
        self,
        key: str,
        local_file: str,
        remote_file: str,
    ) -> None:
        self._retrieve(
            key,
            PurePosixPath(remote_file),
            Path(local_file),
        )

    def _remove(self, remote_path: PurePosixPath) -> None:
        if not self.drive.file_exists(remote_path):
            return

        try:
            self.drive.deleted_file_permanently(remote_path)
        except Exception as e:
            msg = f'Could not remove file on drive at {remote_path}: {e}'
            raise RemoteError(msg) from e

    def remove(self, key: str) -> None:
        # remove the key from the remote
        # raise RemoteError if it couldn't be removed
        # note that removing a not existing key isn't considered an error
        key_path = self._get_key_path(key)
        self._remove(key_path)
        # try deleting the top-level hash-dir(s)
        # speculating that we only have a single key in it
        try:
            for f in (key_path.parent, key_path.parent.parent):
                self.drive.deleted_folder_permanently(f, empty_only=True)
        except DriveFSError:
            # we include when it cannot delete the hashdir,
            # presumably it has other keys
            pass

    def removeexport(
        self,
        key: str,  # noqa: ARG002
        remote_file: str,
    ) -> None:
        self._remove(PurePosixPath(remote_file))

    def removeexportdirectory(
        self,
        remote_directory: str,
    ) -> None:
        try:
            self.drive.deleted_folder_permanently(
                PurePosixPath(remote_directory),
                empty_only=False,
            )
        except Exception as e:
            msg = f'Could not remove folder on drive at {remote_directory}: {e}'
            raise RemoteError(msg) from e

    def renameexport(
        self,
        key: str,  # noqa: ARG002
        filename: str,  # noqa: ARG002
        new_filename: str,  # noqa: ARG002
    ) -> None:
        # ATM we are not implementing this. It would need a three-step,
        # depending in the type of rename
        # 1. move to tmp-folder (must be unique to this rename operation)
        # 2. rename file name
        # 3. move to target folder
        # The reason is the inability to move a file on the drive without
        # holding the file base name constant. This causes the potential
        # for naming conflicts in the source/target folder.
        raise UnsupportedRequest


def ensure_login() -> str:
    # ensure we are logged in
    try:
        res = cli.internxt_whoami()
    except FileNotFoundError as e:
        msg = 'Internxt CLI not found'
        raise RemoteError(msg) from e
    except Exception as e:
        msg = str(e)
        raise RemoteError(msg) from e
    return res['login']['user']['username']


def main() -> None:
    master = Master()
    remote = AnnexRemoteInternxt(master)
    master.LinkRemote(remote)

    logger = logging.getLogger()
    logger.addHandler(master.LoggingHandler())

    master.Listen()


if __name__ == '__main__':
    main()
