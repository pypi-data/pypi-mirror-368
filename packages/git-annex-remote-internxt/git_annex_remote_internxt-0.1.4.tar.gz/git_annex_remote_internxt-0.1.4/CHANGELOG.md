# CHANGELOG

# v0.1.4 (2025-08-10)

## 🐛 Bug Fixes

- avoid exception when deleting a folder that does not exist [[6d745a05]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/6d745a05)
- prevent cross-device linking during export of file in Git [[630c4bf3]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/630c4bf3)
- workaround API reporting a just-create folder to not exist [[7b5049ac]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/7b5049ac)

## 📝 Documentation

- tip on avoiding "empty files not allowed" errors [[d9ba9728]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/d9ba9728)
- tracking branch setup for export remotes [[5d283be3]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/5d283be3)
- disambiguate and clarify remote name argument [[834070d8]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/834070d8)
- more on the installation [[af52648c]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/af52648c)

# v0.1.3 (2025-08-09)

## 🐛 Bug Fixes

- actually include package in wheel distribution [[610cb08f]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/610cb08f)

## 📝 Documentation

- fix commit URLs in changelog and template [[f9dc746e]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/f9dc746e)

# v0.1.2 (2025-08-08)

## 🐛 Bug Fixes

- fail properly when asked to create a folder that already exists [[9cca87ca]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/9cca87ca)
- attempt to avoid repeated checks for root folder [[ff794d6f]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/ff794d6f)

## 📝 Documentation

- fix changelog URL [[9f8e50fd]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/9f8e50fd)

# v0.1.1 (2025-08-08)

## 📝 Documentation

- fix PyPI badge [[03a94c7a]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/03a94c7a)
- remove obsolete limitation from README [[8b01ccef]](https://hub.datalad.org/git-annex/git-annex-remote-internxt/commit/8b01ccef)

# v0.1.0 (2025-08-08)

## 💫 New features

- Python function based wrappers around some parts of the Internxt CLI
- `InternxtDrive` class for path-based operations on an Internxt Drive
- git-annex special remote implementation with export-tree capabilities
