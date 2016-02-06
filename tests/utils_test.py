import os
from statikus.utils import pushd


def test_pushd():
    cwd = os.getcwd()
    with pushd('tests'):
        assert os.getcwd() == cwd + '/' + 'tests'
    assert cwd == os.getcwd()


def test_pushd_with_exception():
    cwd = os.getcwd()
    try:
        with pushd('tests'):
            raise Exception('testing...')
    except Exception:
        pass
    assert cwd == os.getcwd()
