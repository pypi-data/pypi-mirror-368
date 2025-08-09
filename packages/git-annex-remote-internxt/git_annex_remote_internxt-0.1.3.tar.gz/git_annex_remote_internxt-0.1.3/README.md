# git-annex remote for the Internxt Drive

[![PyPI version](https://badge.fury.io/py/git-annex-remote-internxt.svg)](https://badge.fury.io/py/git-annex-remote-internxt)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

[Internxt](https://internxt.com/about) is a cloud storage ecosystem with a focus on data security and privacy.
The `git-annex-remote-internxt` provides a [git-annex](https://git-annex.branchable.com) special remote implementation for [Internxt Drive](https://internxt.com/drive), a [GDPR](https://gdpr.eu/what-is-gdpr)-compliant, zero-knowledge-encrypted cloud storage.

## Prerequisites

- An account for [Internxt Drive](https://internxt.com/drive)
- [Internxt CLI](https://github.com/internxt/cli#readme) installation

## Quickstart

Make sure to install the [Internxt CLI](https://github.com/internxt/cli#readme), a CLI tool to interact with Internxt, via `npm`.
Please refer to the tools [installation instructions](https://github.com/internxt/cli#installation) for details.

Once you have a functioning `internxt` CLI, login to your account:

```
internxt login
```

`git-annex-remote-internxt` will use this existing authentication until you `internxt logout`.

Afterwards, you can initialize the special remote within a git-annex repository (replace all placeholders marked with ``<>``):

```
git annex initremote \
    <name> \
    type=external externaltype=internxt encryption=none \
    folder=<UUID-or-path> [exporttree=yes]
```

`folder` is either the UUID of a directory on your Internxt drive (e.g., `uuid:9c9a4251-71b6-11f0-aed5-dc97ba1c2528`), or a relative path to a folder on your drive.
Using a folder UUID can be more robust.
This UUID will not change, even when the folder location is move on the drive (even when moved into the trash).
The folder UUID be taken from the Internxt web UI.
It is part of the URL of the page showing the folder's content.
A path will be resolved to a folder UUID on startup, implying some initial latency.
The advantage of a path-specification is that the respective folder need not exist (yet), and allows for programmatic creation of (many) annex remote deposits, following a particular pattern, without manual interaction with the Internxt Drive.

`encryption` is set to `none`, because the Internxt Drive CLI already does client-side encryption.
Technically it is possible to use it with additional git-annex driven encryption.

Setting the optional `exporttree=yes` enables git-annex's [export mode](https://git-annex.branchable.com/git-annex-export), which allows for representing a regular file tree of a repository on the Internxt Drive.

## Examples

Initialize using a particular Internxt Drive folder (by UUID) as a `internxt` remote (here using export-mode).
The UUID of a folder is shown in the URL of the Drive web UI,after navigating to the folder.
Consequently, the folder must already exist.

```
git annex initremote \
    internxt \
    type=external externaltype=internxt encryption=none \
    folder=uuid:b488fd99-348f-4a91-af24-2fce42ca82ae exporttree=yes
```

Instead of a folder node UUID, a path can be used (here `examples/simple`).
The given path is relative to the root of the Internxt Drive:

```
git annex initremote \
    internxt \
    type=external externaltype=internxt encryption=none \
    folder=examples/simple exporttree=yes
```

After initialization, `git annex copy|drop|get` can be used as usual.
See the [git-annex documentation](https://git-annex.branchable.com/git-annex-export) on how to set up a tracking branch for an export-mode remote, to be able to use `git annex push`.

With a configured special remote, adding the following configuration *also* enables using the remote as a regular Git remote (for `git push|pull`).

```
git config remote.name.url annex::
```

This offer a complete setup that allows for depositing the repository along side its annex keys on an Internxt Drive.
See the [git-annex documentation](https://git-annex.branchable.com/git-remote-annex) for more information.

## Limitations

At the moment, the special remote implementation builds on the Internxt CLI.
This prevents, for example, reporting upload/download progress, or resuming interrupted downloads.
In the future, this could change to a direct usage of the [Internxt Drive API](https://api.internxt.com/drive).
A (presently work-in-progress) [Go library](https://github.com/StarHack/go-internxt-drive) documents the feasibility of such an approach.

The Internxt Drive imposes limitations on some use cases:

- Inability to upload empty files (see [issue](https://github.com/internxt/cli/issues/285))
- Inability to rename a file including the extension (see [issue](https://github.com/internxt/cli/issues/327))
- Inability to upload files with different destination names (with the CLI also on download, but check [this issue](https://github.com/internxt/cli/issues/125) for possible updates)

## Alternatives

There is a [work-in-progress PR](https://github.com/rclone/rclone/pull/8556) for adding Internxt Drive support to [rclone](https://rclone.org).
Once accepted, the Internxt Drive could be used via the [git-annex rclone special remote](https://rclone.org/commands/rclone_gitannex).


## FAQ

### I suspect something is wrong. How can I see what drive operations are performed?

If the environment variable `INTERNXT_DEBUG` is set, debug messages will be written to STDERR.
Each line is prefixed with `INXT`, followed by a short random identifier for associating debug messages from a single Internxt CLI call.
The first message (`RUN`) will name the command and its arguments.
Subsequent message indicate a successful execution (`OK`), or an error (`ERROR`).

### What can I do about the error "Bucket id was not provided"?

Log out of the drive and re-login. This should fix it.
