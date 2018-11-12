import copy
from types import GeneratorType
from collections import Counter, OrderedDict, defaultdict
from .blocks import (
    DEFAULT_BLOCK_LEXICON,
    BLOCK_QUOTE_LEXICON,
    LIST_ITEM_LEXICON,
)
from .inlines import DEFAULT_INLINE_LEXICON
from .scanner import Scanner
from .util import keyify, IGNORE
from .renderer.html import HTMLRenderer

BLOCK_QUOTE_SCANNER = Scanner(BLOCK_QUOTE_LEXICON, 'paragraph')
LIST_ITEM_SCANNER = Scanner(LIST_ITEM_LEXICON, 'paragraph')


class MarkdownState(object):
    def __init__(self, max_depth=6):
        self._defs = defaultdict(OrderedDict)
        self._depths = Counter()
        self._max_depth = max_depth

    def increase_depth(self, t):
        self._depths[t] += 1
        return self._depths[t] <= self._max_depth

    def decrease_depth(self, t):
        self._depths[t] -= 1

    def add_def(self, t, key, value):
        if key not in self._defs[t]:
            self._defs[t][key] = value


class Markdown(object):
    def __init__(self, renderer=None, extensions=None,
                 block_lexicon=None, inline_lexicon=None):
        if renderer is None:
            renderer = HTMLRenderer()

        if block_lexicon is None:
            block_lexicon = copy.copy(DEFAULT_BLOCK_LEXICON)

        if inline_lexicon is None:
            inline_lexicon = copy.copy(DEFAULT_INLINE_LEXICON)

        self.block_lexicon = block_lexicon
        self.inline_lexicon = inline_lexicon
        self.renderer = renderer
        self._ast = renderer.IS_AST

        if extensions:
            for install in extensions:
                install(self)

        self.block_scanner = Scanner(block_lexicon, 'paragraph')
        self.inline_scanner = Scanner(inline_lexicon, 'text')

    def scan_iter_block(self, text, scanner, state):
        for t, value in scanner.scan(text):
            parse = getattr(self, 'parse_' + t, None)
            if parse:
                value = parse(value, state)
            yield t, value

    def scan_render_inline(self, text):
        return self._iter_join(
            self.inline_scanner.scan(text),
            lambda o: self._render(*o))

    def parse_block_html(self, value, state):
        tag, attributes, text = value
        # TODO: process text
        html = '<{}{}>{}</{}>\n'.format(tag, attributes or '', text, tag)
        return html

    def parse_block_quote(self, value, state):
        ok = state.increase_depth('block_quote')
        if ok:
            scanner = BLOCK_QUOTE_SCANNER
            value = self.scan_iter_block(value, scanner, state)
        state.decrease_depth('block_quote')
        return value

    def parse_list(self, value, state):
        ok = state.increase_depth('list')
        if ok:
            items, ordered = value
            items = [
                self.parse_list_item(item, state)
                for item in items
            ]
        state.decrease_depth('block_quote')
        return items, ordered

    def parse_list_item(self, value, state):
        scanner = LIST_ITEM_SCANNER
        return self.scan_iter_block(value, scanner, state)

    def parse_def_link(self, value, state):
        k = keyify(value[0])
        state.add_def('link', k, value)
        return IGNORE

    def parse_def_footnote(self, value, state):
        k = keyify(value[0])
        state.add_def('footnote', k, value)
        return IGNORE

    def render_table(self, headers, body):
        head_cells = []
        for h, align in headers:
            h = self.scan_render_inline(h)
            cell = self.renderer.table_cell(h, th=True, align=align)
            head_cells.append(cell)

        rows = []
        for row in body:
            row_cells = []
            for t, align in row:
                t = self.scan_render_inline(t)
                cell = self.renderer.table_cell(t, align=align)
                row_cells.append(cell)
            rows.append(self.renderer.table_row(row_cells))

        thead = self.renderer.table_row(head_cells)
        return self.renderer.table(thead, rows)

    def render_list(self, items, ordered):
        items = [self._render('list_item', v) for v in items]
        return self.renderer.list(items, ordered)

    def render_paragraph(self, text):
        text = self.scan_render_inline(text)
        return self.renderer.paragraph(text)

    def output(self, text, state):
        if self._ast:
            rv = []
        else:
            rv = ''
        for t, v in self.scan_iter_block(text, self.block_scanner, state):
            if v is IGNORE:
                continue
            o = self._render(t, v)
            if self._ast:
                rv.append(o)
            else:
                rv += o
        return rv

    def _render(self, t, v):
        if isinstance(v, GeneratorType):
            v = self._iter_join(v, lambda o: self._render(*o))

        render = getattr(self, 'render_' + t, None)
        if not render:
            render = getattr(self.renderer, t)
        return _call_value(render, v)

    def _iter_join(self, values, func):
        if self._ast:
            return [func(v) for v in values]
        return ''.join(func(v) for v in values)

    def __call__(self, text, state=None):
        if state is None:
            state = MarkdownState()
        return self.output(text, state)


def _call_value(func, value):
    if value is None:
        return func()
    elif isinstance(value, tuple):
        return func(*value)
    return func(value)
