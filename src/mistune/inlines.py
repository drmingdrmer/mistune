from .consts import HTML_TAGNAME, HTML_ATTRIBUTES

#: escape symbols like: ``\* \+ \! ....``
ESCAPE = r'''\\([\\!"#$%&'()*+,.\/:;<=>?@\[\]^`{}|_~-])'''

AUTO_EMAIL = (
    r'''<([a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@'''
    r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
    r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)>'
)
AUTO_LINK = r'<([A-Za-z][A-Za-z0-9.+-]{1,31}:[^<>\x00-\x20]*)>'

#: link or image syntax::
#:
#: [text](/link "title")
#: ![alt](/src "title")
STD_LINK = (
    r'!?\[('
    r'(?:\[[^^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*'
    r')\]\(\s*'
    r'(?P<link_url><)?([\s\S]*?)(?(link_url)>)'
    r'''(?:\s+(?P<link_quote>['"])([\s\S]*?)(?P=link_quote))?\s*'''
    r'\)'
)

#: Get link from references. References are defined in DEF_LINK in blocks.
#: The syntax looks like::
#:
#:    [an example][id]
#:
#:    [id]: https://example.com "optional title"
REF_LINK = (
    r'!?\[('
    r'(?:\[[^^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*'
    r')\]\s*\[([^^\]]*)\]'
)

#: simple form of reference link::
#:
#:    [an example]
#:
#:    [an example]: https://example.com "optional title"
ALT_REF_LINK = r'!?\[((?:\[[^\]]*\]|[^\[\]])*)\]'

URL_LINK = r'''(https?:\/\/[^\s<]+[^<.,:;"')\]\s])'''

#: emphasis with * or _::
#:
#:    *em*
#:    **strong**
#:    ***strong and em***
EMPHASIS = (
    r'(?P<emphasis_symbol>[\*_]{1,3})'
    r'([\s\S]+?)(?P=emphasis_symbol)'
)

CODESPAN = (
    r'(?P<code_symbol>`+)\s*([\s\S]*?[^`])\s*(?P=code_symbol)(?!`)'  # `code`
)

#: linebreak leaves two spaces at the end of line
LINEBREAK = r' {2,}\n(?!\s*$)'

#: strike through syntax looks like: ``~~word~~``
STRIKETHROUGH = r'~~(?=\S)([\s\S]*?\S)~~'

#: footnote syntax looks like::
#:
#:    [^key]
FOOTNOTE = r'\[\^([^\]]+)\]'

HTML_COMMENT = r'<!--[\s\S]*?-->'
INLINE_HTML = (
    r'<(?P<tag_name>' + HTML_TAGNAME + r')' + HTML_ATTRIBUTES
    + r'\s*>[\s\S]*?<\/(?P=tag_name)>'
)
INLINE_CLOSE_HTML = (
    r'<(' + HTML_TAGNAME + r')' + HTML_ATTRIBUTES + r'\s*\/?>'
)


def parse_escape(m):
    text = m.group(1)
    return 'escape', text


def parse_email(m):
    email = m.group(1)
    return 'email', email


def parse_auto_link(m):
    link = m.group(1)
    return 'link', (link, None, None)


def parse_std_link(m):
    line = m.group(0)
    text = m.group(1)
    link = m.group(3)
    title = m.group(4)
    if line[0] == '!':
        return 'image', (link, text, title)
    return 'link', (link, text, title)


def parse_ref_link(m):
    line = m.group(0)
    text = m.group(1)
    key = m.group(2)
    if not key:
        key = text

    if line[0] == '!':
        return 'ref_image', (key, text)
    return 'ref_link', (key, text)


def parse_url_link(m):
    link = m.group(0)
    return 'link', (link, None, None)


def parse_footnote(m):
    key = m.group(1)
    return 'footnote', key


def parse_emphasis(m):
    level = len(m.group(1))
    text = m.group(2)
    return 'emphasis', (text, level)


def parse_codespan(m):
    code = m.group(2)
    return 'codespan', code


def parse_strikethrough(m):
    text = m.group(1)
    return 'strikethrough', text


def parse_linebreak(m):
    return 'linebreak', None


def parse_inline_html(m):
    tag = m.group(1)
    html = m.group(0)
    return 'inline_html', (tag, html)


def parse_html_comment(m):
    html = m.group(0)
    return 'inline_html', (None, html)


DEFAULT_INLINE_LEXICON = [
    (ESCAPE, parse_escape),
    (AUTO_EMAIL, parse_email),
    (AUTO_LINK, parse_auto_link),
    (URL_LINK, parse_url_link),
    (FOOTNOTE, parse_footnote),
    (STD_LINK, parse_std_link),
    (REF_LINK, parse_ref_link),
    (ALT_REF_LINK, parse_ref_link),
    (EMPHASIS, parse_emphasis),
    (CODESPAN, parse_codespan),
    (STRIKETHROUGH, parse_strikethrough),
    (LINEBREAK, parse_linebreak),
]
