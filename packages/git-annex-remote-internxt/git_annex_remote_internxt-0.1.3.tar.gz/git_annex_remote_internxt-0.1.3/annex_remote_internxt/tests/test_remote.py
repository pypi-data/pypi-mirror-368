from annex_remote_internxt.git import (
    call_git,
)


def test_remote(internxt, annexrepo):
    res = call_git(
        [
            'annex',
            'initremote',
            'internxt',
            'type=external',
            'externaltype=internxt',
            'encryption=none',
            f'folder=uuid:{internxt}',
        ],
        capture_output=True,
        cwd=annexrepo,
        force_c_locale=True,
        text=True,
    )
    assert 'ok' in res
    call_git(
        ['annex', 'testremote', 'internxt', '--fast'],
        cwd=annexrepo,
        force_c_locale=True,
    )
