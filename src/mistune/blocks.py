import re

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

BLOCK_HTML = ''

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


def parse_heading(m):
    text = m.group(1)
    level = len(m.group(0))
    return 'heading', (text, level)


def parse_lheading(m):
    text = m.group(0)
    c = m.group(1)[0]
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


def parse_table(m):
    headers, aligns = _process_table(m.group(1), m.group(2))

    cells = re.sub(r'(?: *\| *)?\n$', '', m.group(3))
    cells = cells.split('\n')
    for i, v in enumerate(cells):
        v = re.sub(r'^ *\| *| *\| *$', '', v)
        cells[i] = re.split(r' *(?<!\\)\| *', v)

    cells = _process_cells(cells)
    return 'table', (headers, aligns, cells)


def parse_nptable(m):
    headers, aligns = _process_table(m.group(1), m.group(2))

    cells = re.sub(r'\n$', '', m.group(3))
    cells = cells.split('\n')
    for i, v in enumerate(cells):
        cells[i] = re.split(r' *(?<!\\)\| *', v)

    cells = _process_cells(cells)
    return 'table', (headers, aligns, cells)


def _process_table(header, align):
    header = _TABLE_HEADER_SUB.sub('', header)
    headers = _TABLE_HEADER_SPLIT.split(header)
    align = _TABLE_ALIGN_SUB.sub('', align)
    aligns = _TABLE_ALIGN_SPLIT.split(align)

    for i, v in enumerate(aligns):
        if _TABLE_ALIGN_RIGHT.search(v):
            aligns[i] = 'right'
        elif _TABLE_ALIGN_CENTER.search(v):
            aligns[i] = 'center'
        elif _TABLE_ALIGN_LEFT.search(v):
            aligns[i] = 'left'
        else:
            aligns[i] = None

    return headers, aligns


def _process_cells(cells):
    for i, line in enumerate(cells):
        for c, cell in enumerate(line):
            # de-escape any pipe inside the cell here
            cells[i][c] = _TABLE_CELL_SUB.sub('|', cell)

    return cells


def parse_block_quote(m):
    text = m.group(0)
    text = _BLOCK_QUOTE_LEADING.sub('', text)
    return 'block_quote', text


def parse_unordered_list(m):
    text = m.group(0)
    items = list(_parse_list_item(
        text, _UNORDERED_LIST_ITEM, _UNORDERED_LIST_BULLET))
    return 'unordered_list', items


def parse_ordered_list(m):
    text = m.group(0)
    items = list(_parse_list_item(
        text, _ORDERED_LIST_ITEM, _ORDERED_LIST_BULLET))
    return 'ordered_list', items


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


RULES = {
    'heading': (HEADING, parse_heading),
    'lheading': (LHEADING, parse_lheading),
    'fences': (FENCES, parse_fences),
    'block_code': (BLOCK_CODE, parse_block_code),
    'hrule': (HRULE, parse_hrule),
    'table': (TABLE, parse_table),
    'nptable': (NPTABLE, parse_nptable),
    'block_quote': (BLOCK_QUOTE, parse_block_quote),
    'unordered_list': (UNORDERED_LIST, parse_unordered_list),
    'ordered_list': (ORDERED_LIST, parse_ordered_list),
    'def_link': (DEF_LINK, parse_def_link),
    'def_footnote': (DEF_FOOTNOTE, parse_def_footnote),
}
