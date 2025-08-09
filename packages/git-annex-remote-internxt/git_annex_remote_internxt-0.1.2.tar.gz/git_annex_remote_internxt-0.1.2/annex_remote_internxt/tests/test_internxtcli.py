import subprocess
import uuid

import pytest

from annex_remote_internxt.internxt_cli import (
    InternxtError,
    call_internxt,
    internxt_config,
    internxt_list,
    internxt_whoami,
)


def _check_result_type(res, t=dict):
    """
    Assert that res conforms to a given type (e.g., a dict).
    """
    assert isinstance(res, t)


def _check_for_desired_props(
    desired_props: list,
    res: dict,
):
    """
    Assert that properties in desired_props are keys in res.
    """
    for prop in desired_props:
        assert res.get(prop, {})


def test_call_internxt_invalid_command(internxt):  # noqa ARG001
    with pytest.raises(subprocess.CalledProcessError):
        call_internxt('invalid_command')


def test_call_internxt_error_message(internxt):  # noqa ARG001
    with pytest.raises(InternxtError, match='must be a valid v4'):
        # list using a non-V4 folder UUID, must fail with 'not valid'
        internxt_list(uuid.uuid1())


def test_call_internxt(internxt):
    out = call_internxt('whoami')
    _check_result_type(out)
    # we must have gotten a UUID to get here
    assert internxt


def test_internxt_whoami(internxt):  # noqa ARG001
    out = internxt_whoami()
    _check_result_type(out)
    # test for relevant properties in the output
    desired_props = ['email', 'rootFolderId', 'username', 'uuid']
    _check_for_desired_props(desired_props, out['login']['user'])


def test_internxt_config(internxt):  # noqa ARG001
    out = internxt_config()
    _check_result_type(out)
    # test for relevant properties in the output
    desired_props = ['Email', 'Root folder ID', 'Used space', 'Available space']
    _check_for_desired_props(desired_props, out['config'])
