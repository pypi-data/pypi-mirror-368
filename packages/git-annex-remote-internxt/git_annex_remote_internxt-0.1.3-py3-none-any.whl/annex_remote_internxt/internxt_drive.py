"""Convenience API for interaction with an Internxt Drive"""
# This module should not be concerned with any direct interfacing with
# CLI subprocesses or JSON-str output processing

from dataclasses import (
    dataclass,
    field,
)
from pathlib import (
    Path,
    PurePosixPath,
)
from typing import (
    Any,
    TypeVar,
)
from uuid import (
    UUID,
    uuid4,
)

import annex_remote_internxt.internxt_cli as cli
from annex_remote_internxt.internxt_cli import (
    InternxtError,
)


class _Unset:
    """Utility type to indicate an unset value"""


# from PY3.11 on this just becomes `Self`
DriveNodeT = TypeVar('DriveNodeT', bound='DriveNode')
DriveFolderT = TypeVar('DriveFolderT', bound='DriveFolder')


@dataclass
class DriveNode:
    """Record in a drive folder listing"""

    uuid: UUID
    name: str
    kind: str

    @classmethod
    def from_listing(
        cls: type[DriveNodeT],
        item: dict[str, Any],
    ) -> DriveNodeT:
        return DriveNode(
            uuid=UUID(item['uuid']),
            name=item['plainName'],
            # we need 'type' for files, it is the file name extension
            kind=item['type'],
        )


@dataclass
class DriveFolder:
    """Drive folder content (listing)"""

    # None represents the drive root
    uuid: UUID | None
    files: list[DriveNode] = field(default_factory=list)
    folders: list[DriveNode] = field(default_factory=list)

    @classmethod
    def from_listing(
        cls: type[DriveFolderT],
        folder_uuid: UUID | None,
    ) -> DriveFolderT:
        lst = cli.internxt_list(folder_uuid)
        folder = DriveFolder(uuid=folder_uuid)
        for t in ('folders', 'files'):
            setattr(folder, t, [DriveNode.from_listing(r) for r in lst[t]])
        return folder


class DriveFSError(Exception):
    """This exception is raised for filesystem-related errors on the Drive,
    including attempts to remove a non-empty directory, create or remove the
    root folder, or “file/directory not found” errors."""


class InternxtDrive:
    """ """

    def __init__(self, root_folder_id: UUID | None = None) -> None:
        """ """
        self._root_folder_id = root_folder_id
        # mapping of folder paths to their content listings,
        # used as a cache to minimize API requests.
        # the root_folder_id matches the path '.'
        self._list_cache: dict[PurePosixPath, DriveFolder] = {}

    @property
    def root_folder_id(self) -> UUID | None:
        return self._root_folder_id

    def get_folder_id(self, path: PurePosixPath) -> UUID | None:
        if path == PurePosixPath():
            return self._root_folder_id

        lst = self._get_listing(path.parent)
        node = match_record(lst.folders, name=path.name)
        if not node:
            msg = f'a folder at {path} does not exist'
            raise DriveFSError(msg)
        return node.uuid

    def _get_listing(
        self,
        path: PurePosixPath,
    ) -> DriveFolder:
        """
        Raise ``DriveFSError`` if the ``path`` or any of its
        parents does not exist in the drive.
        """
        lst = self._list_cache.get(path)
        if lst is not None:
            return lst

        closest_known_path = path
        # until we reached the root folder,
        # find the closest folder listing, so we can start
        # going down the tree to get the requested listing
        while lst is None:
            lst = self._list_cache.get(closest_known_path)
            if lst is not None:
                break
            if closest_known_path == PurePosixPath():
                # we reached the root
                break
            closest_known_path = closest_known_path.parent

        curr_path = closest_known_path
        if lst is None:
            # we got nothing at all, start with the root
            lst = DriveFolder.from_listing(self.root_folder_id)
            self._list_cache[PurePosixPath()] = lst
        # now move down to the target path
        for p in path.relative_to(closest_known_path).parts:
            curr_path = curr_path / p
            node = match_record(lst.folders, name=p)
            folder_uuid = node.uuid if node else None
            if folder_uuid is None:
                msg = f"'{curr_path}' is not an existing folder"
                raise DriveFSError(msg)
            lst = DriveFolder.from_listing(folder_uuid)
            self._list_cache[curr_path] = lst
        return lst

    def create_folder(
        self,
        path: PurePosixPath,
        *,
        parents: bool = False,
        exists_ok: bool = False,
    ) -> None:
        """ """
        if path == PurePosixPath():
            # root folder always exists
            if exists_ok:
                return
            msg = 'Cannot create root folder'
            raise DriveFSError(msg)

        if self.folder_exists(path):
            if exists_ok:
                return
            msg = f"Folder '{path}' already exists"
            raise DriveFSError(msg)

        if parents and len(path.parts) > 1 and not self.folder_exists(path.parent):
            # recursively create the parents
            self.create_folder(
                path.parent,
                parents=True,
            )

        # at this point the parent folder either exists, or we can
        # fail if it doesn't exist
        if path.parent != PurePosixPath() and not self.folder_exists(path.parent):
            msg = f'Parent folder of {path} does not exist'
            raise DriveFSError(msg)

        parent_id = self._get_listing(path.parent).uuid
        try:
            res = cli.internxt_create_folder(
                path.name,
                parent_id,
            )
            # folder now exists, update listing cache
            self._list_cache[path] = DriveFolder(uuid=res['uuid'])
            self._list_cache[path.parent].folders.append(
                DriveNode(
                    uuid=UUID(res['uuid']),
                    name=path.name,
                    kind='folder',
                )
            )
        except InternxtError:
            # something went wrong, it might be that the folder
            # already exists
            if not exists_ok or not self.folder_exists(path):
                raise

    def folder_exists(self, path: PurePosixPath) -> bool:
        """ """
        if path == PurePosixPath():
            # special case: we cannot rely on a listing to fail
            # for a non existing root path. it will happily report
            # and empty folder. instead we attempt to create a subfolder
            # and what that fail or not
            res = None
            probe_name = f'__probe_{uuid4()}'
            try:
                res = cli.internxt_create_folder(
                    probe_name,
                    self.root_folder_id,
                )
            except InternxtError:
                return False
            else:
                return True
            finally:
                if res is not None:
                    cli.internxt_delete_permanently_folder(res['uuid'])
        try:
            self._get_listing(path)
        except DriveFSError:
            return False
        else:
            return True

    def file_exists(self, path: PurePosixPath) -> bool:
        """ """
        # this is not a duplicate request, it would just fetch the
        # necessary listings if still needed.
        # we avoid checking for the existence of the root folder.
        # its absence is rather unlikely and the test for its presence
        # it a very expensive special case
        if path.parent != PurePosixPath() and not self.folder_exists(path.parent):
            return False
        # now just look at the listing, we know exists at this point
        lst = self._get_listing(path.parent)
        node = match_record(
            lst.files,
            name=path.stem,
            kind=get_fkind(path),
        )
        return node is not None

    def upload(self, src: Path, dest_folder: PurePosixPath) -> UUID:
        """ """
        # we avoid checking for the existence of the root folder.
        # its absence is rather unlikely and the test for its presence
        # it a very expensive special case
        if dest_folder.parent != PurePosixPath() and not self.folder_exists(
            dest_folder
        ):
            msg = f'Target folder {dest_folder} does not exist'
            raise ValueError(msg)

        lst = self._get_listing(dest_folder)
        # efficiency short cut, if target file does not exist
        # no transfer location is needed
        if not self.file_exists(dest_folder / src.name):
            res = cli.internxt_upload_file(
                src,
                self.get_folder_id(dest_folder),
            )
            fuuid = UUID(res['uuid'])
            # must construct by hand (not .from_listing)
            # there is no plainName, just name
            # https://github.com/internxt/cli/issues/328
            lst.files.append(
                DriveNode(
                    uuid=fuuid,
                    name=res['name'],
                    kind=res['type'],
                )
            )
            return fuuid

        # we have a file in the location we want to upload to
        # go with a temporary transfer folder, upload there first,
        # then move, then remove the tmp folder
        transfer_folder_path = PurePosixPath(f'.transfer-{uuid4()}')
        # wrap in try-finally to ensure transfer folder is
        # removed again
        try:
            self.create_folder(transfer_folder_path)
            res = cli.internxt_upload_file(
                src,
                self.get_folder_id(transfer_folder_path),
            )
            file_id = UUID(res['uuid'])
            target_path = dest_folder / src.name
            # we know there is a file in the target location already
            self.deleted_file_permanently(target_path)

            # need not delete and remove from cache, the entire transfer
            # folder goes away in finally
            cli.internxt_move_file(
                file_id,
                self._get_listing(dest_folder).uuid,
            )
        finally:
            self.deleted_folder_permanently(
                transfer_folder_path,
                # even when the upload is still in there,
                # speculating that no one fixes it by hand,
                # but most people prefer a clean deposit
                # without accumulating cruft
                empty_only=False,
            )

        fuuid = UUID(res['uuid'])
        # must construct by hand (not .from_listing)
        # there is no plainName, just name
        # https://github.com/internxt/cli/issues/328
        lst.files.append(
            DriveNode(
                uuid=fuuid,
                name=res['name'],
                kind=res['type'],
            )
        )
        return fuuid

    def download(self, src: PurePosixPath, dest_dir: Path):
        """ """
        if not self.file_exists(src):
            msg = f'{src} does not exist in the drive'
            raise DriveFSError(msg)
        lst = self._get_listing(src.parent)
        node = match_record(
            lst.files,
            name=src.stem,
            kind=get_fkind(src),
        )
        cli.internxt_download_file(
            node.uuid if node else None,
            dest_dir,
        )

    def deleted_folder_permanently(
        self,
        path: PurePosixPath,
        *,
        empty_only: bool = True,
    ):
        """ """
        if path == PurePosixPath():
            msg = 'Deleting the root folder is not supported'
            raise DriveFSError(msg)
        lst = self._get_listing(path)

        # TODO: maybe test for `empty_only` should not just use
        # cache knowledge, but an actual API request
        # -- given that this is "permanently"
        if empty_only and (len(lst.folders) or len(lst.files)):
            msg = f'Not deleting folder {path}, it is not empty'
            raise DriveFSError(msg)

        cli.internxt_delete_permanently_folder(lst.uuid)

        # remove this folder and all its children from the cache
        self._list_cache = {
            k: v
            for k, v in self._list_cache.items()
            if not (path == k or path in k.parents)
        }
        # and remove it as a subfolder in it's parent
        self._list_cache[path.parent].folders = [
            i for i in self._list_cache[path.parent].folders if i.name != path.name
        ]

    def deleted_file_permanently(self, path: PurePosixPath):
        """ """
        lst = self._get_listing(path.parent)
        node = match_record(
            lst.files,
            name=path.stem,
            kind=get_fkind(path),
        )
        if not node:
            # doesn't exist, return happy
            return
        cli.internxt_delete_permanently_file(node.uuid)
        lst.files = [i for i in lst.files if i.uuid != node.uuid]

    def move_file(self, src: PurePosixPath, dest: PurePosixPath):
        """ """
        # needs to determine from src and dest if this is a
        # move or a rename


def get_fkind(path: PurePosixPath) -> str | None:
    fkind: str | None = path.suffix.lstrip('.')
    if not fkind:
        # we need to normalize this to `None`, because this is
        # how a `list` will report it
        fkind = None
    return fkind


def match_record(
    records: list[DriveNode],
    **kwargs: Any,
) -> DriveNode | None:
    """Return first record matching all key-value constraints"""
    for r in records:
        match = True
        for k, v in kwargs.items():
            if getattr(r, k, _Unset) != v:
                match = False
                break
        if match:
            return r
    return None
