from pathlib import Path

from annex_remote_internxt.git import (
    call_git,
)
from annex_remote_internxt.internxt_cli import (
    internxt_list,
)


def test_test_root_uuid(internxt):
    # internxt returns the internxt_testroot_uuid, or skips the
    # test if the internxt system is unavailable
    internxt_list(internxt)


def test_annexrepo(annexrepo):
    res = call_git(
        ['annex', 'info'],
        capture_output=True,
        cwd=annexrepo,
        force_c_locale=True,
        text=True,
    )
    assert '[here]' in res


def test_populated_annexrepo(populated_annexrepo):
    # test that all expected files and directories are present
    files = ['file1.txt', 'file2.csv', 'subdir/file1.txt', 'subdir/subsubdir/file2.csv']
    dirs = ['subdir', 'subdir/subsubdir']
    for file in files:
        assert (populated_annexrepo / Path(file)).exists()
        assert (populated_annexrepo / Path(file)).is_file()
        # check file content
        content = f'content of {file}'
        assert content == (populated_annexrepo / Path(file)).read_text()
    for d in dirs:
        assert (populated_annexrepo / Path(d)).is_dir()
    # check that everything is properly annexed
    res = call_git(
        ['annex', 'info'],
        capture_output=True,
        cwd=populated_annexrepo,
        force_c_locale=True,
        text=True,
    )
    assert 'local annex keys: 4' in res
