import re
from .exceptions import URLParseException


variable_pattern = re.compile('<(.*?)\>')
wildcard_pattern = re.compile('\*')
valid_chars_pattern = re.compile('^[0-9a-zaA-Z\-\__\/\.]*$')


def is_variable(url_pattern):
    return (
        wildcard_pattern.search(url_pattern) is not None or
        variable_pattern.search(url_pattern) is not None)


def cleanup(url, append_slashes=True, ommit_valid_chars_error=False):
    if append_slashes and url[-1] != '/' and '.' not in url.split('/')[-1]:
        url += '/'
    if append_slashes and url[0] != '/':
        url = '/' + url

    if not ommit_valid_chars_error and not valid_chars_pattern.match(url):
        raise URLParseException("The URL contains non-standart characters!")

    return url


def process_variable_url(url_pattern, variable_replacements, custom_url):
    """
    """
    url = url_pattern

    if wildcard_pattern.search(url_pattern):
        if variable_pattern.search(url_pattern):
            raise URLParseException("You can't combine wildcards and variables in a URL")
        url = wildcard_pattern.sub(custom_url, url_pattern)
    elif variable_pattern.search(url_pattern):
        replace_keys = variable_pattern.findall(url_pattern)
        missing_keys = [key for key in replace_keys if key not in variable_replacements]
        if len(missing_keys) > 0:
            raise URLParseException("Missing URL replacements: %s" % missing_keys)
        for key in replace_keys:
            url = variable_pattern.sub(variable_replacements[key], url, count=1)

    return url
