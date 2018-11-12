import re

_escape_pattern = re.compile(r'&(?!#?\w+;)')
_scheme_blacklist = ('javascript:', 'vbscript:')


class _Ignore(object):
    pass


IGNORE = _Ignore()


def keyify(key):
    key = escape(key.lower(), quote=True)
    return re.sub(r'\s+', ' ', key)


def escape(text, quote=False, smart_amp=True):
    """Replace special characters "&", "<" and ">" to HTML-safe sequences.

    The original cgi.escape will always escape "&", but you can control
    this one for a smart escape amp.

    :param quote: if set to True, " and ' will be escaped.
    :param smart_amp: if set to False, & will always be escaped.
    """
    if smart_amp:
        text = _escape_pattern.sub('&amp;', text)
    else:
        text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    if quote:
        text = text.replace('"', '&#34;')
        text = text.replace("'", '&#39;')
    return text


def escape_link(url):
    """Remove dangerous URL schemes like javascript: and escape afterwards."""
    lower_url = url.lower().strip('\x00\x1a \n\r\t')

    for scheme in _scheme_blacklist:
        if re.sub(r'[^A-Za-z0-9\/:]+', '', lower_url).startswith(scheme):
            return ''
    return escape(url, quote=True, smart_amp=False)
