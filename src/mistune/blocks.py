import re
from .consts import HTML_TAGNAME, HTML_ATTRIBUTES

#: just blank lines
NEWLINE = r'\n+'

#: headings like::
#:
#:    ## level 2 title
HEADING = r'(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)'

#: headings like::
#:
#:    level 1 title
#:    =============
LHEADING = r'([^\n]+)\n(=+|-+) *(?:\n+|$)'

#: fences code like::
#:
#:    ```python
#:    def foo():
#:        return 'bar'
#:    ```
FENCES = (
    r'(?P<fences_symbol>`{3,}|~{3,}) *([^`\s]+)? *\n'  # ```lang
    r'([\s\S]+?)\s*'
    r'(?P=fences_symbol) *(?:\n+|$)'  # ```
)

#: block code with 4 spaces indentation
BLOCK_CODE = r'(?: {4}[^\n]+\n*)+'
_BLOCK_CODE_LEADING = re.compile(r'^ {4}', re.M)

#: <hr> rule like: ``* * *``
HRULE = r' {0,3}(?P<hr>-|\*|_)(?: *(?P=hr)){2,} *(?:\n+|$)'

BLOCK_HTML = (
    r' *<(?P<tag_name>' + HTML_TAGNAME + r')'
    r'(' + HTML_ATTRIBUTES + r')'
    r'\s*>([\s\S]*?)<\/(?P=tag_name)> *(?:\n+|$)'
)


#: normal table format like::
#:
#:    | Heading 1 | Heading 2
#:    | --------- | ---------
#:    | Cell 1    | Cell 2
#:    | Cell 3    | Cell 4
TABLE = (
    r'\|(.+)\n'
    r'\|( *[-:]+[-| :]*)\n'
    r'((?: *\|.*(?:\n|$))*)\n*'
)

#: simple table format like::
#:
#:    Header 1 | Header 2
#:    -------- | --------
#:    Cell 1   | Cell 2
#:    Cell 3   | Cell 4
NPTABLE = (
    r'(\S.*\|.*)\n'
    r'([-:]+ *\|[-| :]*)\n'
    r'((?:.*\|.*(?:\n|$))*)\n*'
)

_TABLE_HEADER_SUB = re.compile(r'^ *| *\| *$')
_TABLE_HEADER_SPLIT = re.compile(r' *\| *')
_TABLE_ALIGN_SUB = re.compile(r' *|\| *$')
_TABLE_ALIGN_SPLIT = re.compile(r' *\| *')
_TABLE_ALIGN_RIGHT = re.compile(r'^ *-+: *$')
_TABLE_ALIGN_CENTER = re.compile(r'^ *:-+: *$')
_TABLE_ALIGN_LEFT = re.compile(r'^ *:-+ *$')
_TABLE_CELL_SUB = re.compile(r'\\\|')

#: block quote syntax like::
#:
#:    > block quote
BLOCK_QUOTE = r'(?:>[^\n]+(?:\n[^\n]+)*\n*)+'
_BLOCK_QUOTE_LEADING = re.compile(r'^> ?', flags=re.M)

#: unordered list syntax like::
#:
#:    * item 1
#:    * item 2
UNORDERED_LIST = (
    r'(?P<list_space> *)(?P<list_symbol>[*+-]) [^\n]*'
    r'(?:'
    r'(?:\n(?P=list_space)(?P=list_symbol) [^\n]*)|'  # same bullet
    r'(?:\n(?P=list_space) +[^\n]*)|'  # indent
    r'(?:\n *)|'
    r')*'
    r'(?:\n+|\$)'
)
_UNORDERED_LIST_ITEM = re.compile(
    r'(^(?P<list_space> *)[*+-] [^\n]*'
    r'(?:(?:\n(?P=list_space) +[^\n]*)|(?:\n *))*'
    r'(?:\n+|\$))',
    flags=re.M
)
_UNORDERED_LIST_BULLET = re.compile(r'^ *[*+-] +')

#: ordered list syntax like::
#:
#:    1. item 1
#:    2. item 2
ORDERED_LIST = (
    r'(?P<list_space> *)\d+\. [^\n]*'
    r'(?:'
    r'(?:\n(?P=list_space)(?: +|\d+\.)[^\n]*)|'
    r'(?:\n *)|'
    r')*'
    r'(?:\n+|\$)'
)
_ORDERED_LIST_ITEM = re.compile(
    r'(^(?P<list_space> *)\d+\. [^\n]*'
    r'(?:(?:\n(?P=list_space) +[^\n]*)|(?:\n *))*'
    r'(?:\n+|\$))',
    flags=re.M
)
_ORDERED_LIST_BULLET = re.compile(r'^ *\d+\. +')

#: def links syntax like::
#:
#:    [key]: https://example.com "title"
DEF_LINK = (
    r' *\[([^^\]]+)\]: *'  # [key]:
    r'<?([^\s>]+)>?'  # <link> or link
    r'(?: +["(]([^\n]+)[")])? *(?:\n+|$)'  # "title"
)
#: def footnotes syntax like::
#:
#:    [^key]: footnote text
DEF_FOOTNOTE = (
    r'\[\^([^\]]+)\]: *('  # [^key]:
    r'[^\n]*(?:\n+|$)'
    r'(?: {1,}[^\n]*(?:\n+|$))*'
    r')'
)


def parse_newline(m):
    return 'newline', None


def parse_heading(m):
    level = len(m.group(1))
    text = m.group(2)
    return 'heading', (text, level)


def parse_lheading(m):
    text = m.group(1)
    c = m.group(2)[0]
    if c == '=':
        level = 1
    else:
        level = 2
    return 'heading', (text, level)


def parse_fences(m):
    lang = m.group(2)
    code = m.group(3)
    return 'block_code', (code, lang)


def parse_block_code(m):
    text = m.group(0)
    code = _BLOCK_CODE_LEADING.sub('', text)
    return 'block_code', (code, None)


def parse_hrule(m):
    return 'hrule', None


def parse_block_html(m):
    tag = m.group(1)
    attributes = m.group(2)
    content = m.group(3)
    return 'block_html', (tag, attributes, content)


def parse_table(m):
    headers = list(_process_table_headers(m.group(1), m.group(2)))
    h_len = len(headers)

    rows = re.sub(r'(?: *\| *)?\n$', '', m.group(3))
    rows = rows.split('\n')
    for i, v in enumerate(rows):
        v = re.sub(r'^ *\| *| *\| *$', '', v)
        cells = re.split(r' *(?<!\\)\| *', v)
        for j, cell in enumerate(cells):
            if j < h_len:
                align = headers[j][1]
            else:
                align = None
            # de-escape any pipe inside the cell here
            text = _TABLE_CELL_SUB.sub('|', cell)
            cells[j] = (text, align)
        rows[i] = cells

    return 'table', (headers, rows)


def parse_nptable(m):
    headers = list(_process_table_headers(m.group(1), m.group(2)))
    h_len = len(headers)

    rows = re.sub(r'\n$', '', m.group(3))
    rows = rows.split('\n')
    for i, v in enumerate(rows):
        cells = re.split(r' *(?<!\\)\| *', v)
        for j, cell in enumerate(cells):
            if j < h_len:
                align = headers[j][1]
            else:
                align = None
            # de-escape any pipe inside the cell here
            text = _TABLE_CELL_SUB.sub('|', cell)
            cells[j] = (text, align)
        rows[i] = cells

    return 'table', (headers, rows)


def _process_table_headers(header, align):
    header = _TABLE_HEADER_SUB.sub('', header)
    headers = _TABLE_HEADER_SPLIT.split(header)
    align = _TABLE_ALIGN_SUB.sub('', align)
    aligns = _TABLE_ALIGN_SPLIT.split(align)

    aligns_length = len(aligns)

    for i, h in enumerate(headers):
        if i < aligns_length:
            align = None
            yield h, None
        else:
            av = aligns[i]
            if _TABLE_ALIGN_RIGHT.search(av):
                yield h, 'right'
            elif _TABLE_ALIGN_CENTER.search(av):
                yield h, 'center'
            elif _TABLE_ALIGN_LEFT.search(av):
                yield h, 'left'
            else:
                yield h, None


def parse_block_quote(m):
    text = m.group(0)
    text = _BLOCK_QUOTE_LEADING.sub('', text)
    return 'block_quote', text


def parse_unordered_list(m):
    text = m.group(0)
    items = list(_parse_list_item(
        text, _UNORDERED_LIST_ITEM, _UNORDERED_LIST_BULLET))
    return 'list', (items, False)


def parse_ordered_list(m):
    text = m.group(0)
    items = list(_parse_list_item(
        text, _ORDERED_LIST_ITEM, _ORDERED_LIST_BULLET))
    return 'list', (items, True)


def _parse_list_item(text, item_pattern, bullet_pattern):
    items = item_pattern.findall(text)
    for s, _ in items:
        length = len(s)
        s = bullet_pattern.sub('', s)
        space = length - len(s)
        pattern = re.compile(r'^ {1,%d}' % space, flags=re.M)
        s = pattern.sub('', s)
        yield s


def parse_def_link(m):
    key = m.group(1)
    link = m.group(2)
    title = m.group(3)
    return 'def_link', (key, link, title)


def parse_def_footnote(m):
    key = m.group(1)
    text = m.group(2).strip()

    if '\n' not in text:
        return 'def_footnote', (key, text)

    lines = text.splitlines()
    whitespace = None
    for line in lines[1:]:
        space = len(line) - len(line.lstrip())
        if space and (not whitespace or space < whitespace):
            whitespace = space

    newlines = [lines[0]]
    for line in lines[1:]:
        newlines.append(line[whitespace:])

    text = '\n'.join(newlines)
    return 'def_footnote', (key, text)


# order matters, simple at top
DEFAULT_BLOCK_LEXICON = [
    (NEWLINE, parse_newline),
    (HRULE, parse_hrule),
    (BLOCK_CODE, parse_block_code),
    (FENCES, parse_fences),
    (HEADING, parse_heading),
    (NPTABLE, parse_nptable),
    (LHEADING, parse_lheading),
    (BLOCK_QUOTE, parse_block_quote),
    (UNORDERED_LIST, parse_unordered_list),
    (ORDERED_LIST, parse_ordered_list),
    (DEF_LINK, parse_def_link),
    (DEF_FOOTNOTE, parse_def_footnote),
    (TABLE, parse_table),
    (BLOCK_HTML, parse_block_html),
]

BLOCK_QUOTE_LEXICON = [
    (NEWLINE, parse_newline),
    (HRULE, parse_hrule),
    (BLOCK_CODE, parse_block_code),
    (FENCES, parse_fences),
    (HEADING, parse_heading),
    (LHEADING, parse_lheading),
    (BLOCK_QUOTE, parse_block_quote),
    (UNORDERED_LIST, parse_unordered_list),
    (ORDERED_LIST, parse_ordered_list),
    (DEF_LINK, parse_def_link),
    (DEF_FOOTNOTE, parse_def_footnote),
    (BLOCK_HTML, parse_block_html),
]

LIST_ITEM_LEXICON = [
    (NEWLINE, parse_newline),
    (HRULE, parse_hrule),
    (BLOCK_CODE, parse_block_code),
    (FENCES, parse_fences),
    (HEADING, parse_heading),
    (LHEADING, parse_lheading),
    (BLOCK_QUOTE, parse_block_quote),
    (UNORDERED_LIST, parse_unordered_list),
    (ORDERED_LIST, parse_ordered_list),
    (DEF_LINK, parse_def_link),
    (DEF_FOOTNOTE, parse_def_footnote),
    (BLOCK_HTML, parse_block_html),
]
