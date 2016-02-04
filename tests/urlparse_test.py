import pytest
from statikus import url
from statikus.exceptions import URLParseException


@pytest.mark.parametrize("test_input,expected", [
    ('path/to/nowhere', False),
    ('path/with/invalid<variable/name/', False),
    ('path/to/<somewhere>', True),
    ('path/to/<somewhere>/<else>', True),
    ('path/to/*', True),
    ('path/to/*/nirvana', True),
])
def test_is_variable(test_input, expected):
    assert expected == url.is_variable(test_input)


@pytest.mark.parametrize("test_input,expected", [
    ('path/to/nowhere', '/path/to/nowhere/'),
    ('/path/to/nowhere/', '/path/to/nowhere/'),
    ('path/to/nowhere.txt', '/path/to/nowhere.txt'),
    ('/path/to/nowhere.txt', '/path/to/nowhere.txt'),
])
def test_cleanup(test_input, expected):
    assert expected == url.cleanup(test_input)


def test_cleanup_ommits_error_for_invalid_chars():
    assert '/asd@foo/' == url.cleanup('asd@foo', ommit_valid_chars_error=True)


def test_cleanup_ommits_slashes_when_disabled():
    assert 'i-hate-slashes' == url.cleanup('i-hate-slashes', append_slashes=False)


def test_cleanup_raises_error_for_invalid_chars():
    with pytest.raises(URLParseException) as exceptionInfo:
        url.cleanup('asd@foo')

    # Assert exception message
    assert str(exceptionInfo.value) == 'The URL contains non-standart characters!'


@pytest.mark.parametrize("url_pattern,expected,variable_replacements,custom_url", [
    ('path/<to>/<where>', 'path/my/site', {'to': 'my', 'where': 'site'}, None),
    ('path/<to>/<to>', 'path/my/my', {'to': 'my'}, None),
    ('path/ignore', 'path/ignore', {'to': 'my'}, None),
    ('path/ignore', 'path/ignore', None, 'specific'),
    ('path/*', 'path/specific', None, 'specific'),
    ('path/*/wildcard', 'path/specific/wildcard', None, 'specific'),
])
def test_process_variable_url(url_pattern, expected, variable_replacements, custom_url):
    assert expected == url.process_variable_url(url_pattern, variable_replacements, custom_url)
