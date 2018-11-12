import re
from mistune.util import escape, escape_link


class HTMLRenderer(object):
    IS_AST = False

    def __init__(self, escape=True):
        self._escape = escape
        self.options = {}

    def block_code(self, code, lang=None):
        """Rendering block level code. ``pre > code``.

        :param code: text content of the code block.
        :param lang: language of the given code.
        """
        code = code.rstrip('\n')
        if not lang:
            code = escape(code, smart_amp=False)
            return '<pre><code>' + code + '\n</code></pre>\n'
        code = escape(code, quote=True, smart_amp=False)
        out = '<pre><code class="lang-'
        out += lang + '">'
        return out + code + '\n</code></pre>\n'

    def block_quote(self, text):
        """Rendering <blockquote> with the given text.

        :param text: text content of the blockquote.
        """
        return '<blockquote>' + text.rstrip('\n') + '\n</blockquote>\n'

    def block_html(self, html):
        """Rendering block level pure html content.

        :param html: text content of the html snippet.
        """
        if self.options.get('skip_style') and \
           html.lower().startswith('<style'):
            return ''
        if self._escape:
            return escape(html)
        return html

    def heading(self, text, level, raw=None):
        """Rendering header/heading tags like ``<h1>`` ``<h2>``.

        :param text: rendered text content for the header.
        :param level: a number for the header level, for example: 1.
        :param raw: raw text content of the header.
        """
        tag = 'h' + str(level)
        return '<' + tag + '>' + text + '</' + tag + '>\n'

    def hrule(self):
        """Rendering method for ``<hr>`` tag."""
        return '<hr>\n'

    def list(self, items, ordered=True):
        """Rendering list tags like ``<ul>`` and ``<ol>``.

        :param items: list items.
        :param ordered: whether this list is ordered or not.
        """
        tag = 'ul'
        if ordered:
            tag = 'ol'

        body = ''.join(items)
        return '<%s>\n%s</%s>\n' % (tag, body, tag)

    def list_item(self, text):
        """Rendering list item snippet. Like ``<li>``."""
        return '<li>' + text + '</li>\n'

    def paragraph(self, text):
        """Rendering paragraph tags. Like ``<p>``."""
        return '<p>' + text.strip(' ') + '</p>\n'

    def table(self, head, rows):
        """Rendering table element. Wrap header and body in it.

        :param head: thead part of the table.
        :param rows: body part of the table.
        """
        body = ''.join(rows)
        return (
            '<table>\n<thead>' + head + '</thead>\n'
            '<tbody>\n' + body + '</tbody>\n</table>\n'
        )

    def table_row(self, cells):
        """Rendering a table row. Like ``<tr>``.

        :param content: content of current table row.
        """
        content = ''.join(cells)
        return '<tr>\n' + content + '</tr>\n'

    def table_cell(self, content, **flags):
        """Rendering a table cell. Like ``<th>`` ``<td>``.

        :param content: content of current table cell.
        :param header: whether this is header or not.
        :param align: align of current table cell.
        """
        if flags.get('th'):
            tag = 'th'
        else:
            tag = 'td'
        align = flags.get('align')
        if not align:
            return '<%s>%s</%s>\n' % (tag, content, tag)
        return '<%s style="text-align:%s">%s</%s>\n' % (
            tag, align, content, tag
        )

    def emphasis(self, text, level):
        """Rendering **strong** and _em_ text.

        :param text: text content for emphasis.
        """
        if level == 1:
            return '<em>' + text + '</em>'
        if level == 2:
            return '<strong>' + text + '</strong>'
        return '<strong><em>' + text + '</em></strong>'

    def codespan(self, text):
        """Rendering inline `code` text.

        :param text: text content for inline code.
        """
        text = escape(text.rstrip(), smart_amp=False)
        return '<code>' + text + '</code>'

    def linebreak(self):
        """Rendering line break like ``<br>``."""
        if self.options.get('use_xhtml'):
            return '<br />\n'
        return '<br>\n'

    def strikethrough(self, text):
        """Rendering ~~strikethrough~~ text.

        :param text: text content for strikethrough.
        """
        return '<del>' + text + '</del>'

    def escape(self, text):
        """Rendering escape sequence.

        :param text: text content.
        """
        return escape(text)

    def text(self, text):
        """Rendering unformatted text.

        :param text: text content.
        """
        if self.options.get('parse_block_html'):
            return text
        return escape(text)

    def email(self, email):
        """Rendering a given email address.

        :param email: email address.
        """
        link = 'mailto:' + email
        return '<a href="%s">%s</a>' % (link, email)

    def link(self, link, text, title):
        """Rendering a given link with content and title.

        :param link: href link for ``<a>`` tag.
        :param text: text content for description.
        :param title: title content for `title` attribute.
        """
        if not text:
            text = link
        link = escape_link(link)
        if not title:
            return '<a href="%s">%s</a>' % (link, text)
        title = escape(title, quote=True)
        return '<a href="%s" title="%s">%s</a>' % (link, title, text)

    def image(self, src, text, title):
        """Rendering a image with title and text.

        :param src: source link of the image.
        :param title: title text of the image.
        :param text: alt text of the image.
        """
        src = escape_link(src)
        text = escape(text, quote=True)
        if title:
            title = escape(title, quote=True)
            html = '<img src="%s" alt="%s" title="%s"' % (src, text, title)
        else:
            html = '<img src="%s" alt="%s"' % (src, text)
        if self.options.get('use_xhtml'):
            return '%s />' % html
        return '%s>' % html

    def inline_html(self, tag, html):
        """Rendering inline level html content.

        :param html: text content of the html snippet.
        """
        if self._escape:
            return escape(html)
        return html

    def newline(self):
        """Rendering newline element."""
        if self.options.get('hardwrap'):
            return self.linebreak()
        return ''

    def footnote_ref(self, key, index):
        """Rendering the ref anchor of a footnote.

        :param key: identity key for the footnote.
        :param index: the index count of current footnote.
        """
        html = (
            '<sup class="footnote-ref" id="fnref-%s">'
            '<a href="#fn-%s">%d</a></sup>'
        ) % (escape(key), escape(key), index)
        return html

    def footnote_item(self, key, text):
        """Rendering a footnote item.

        :param key: identity key for the footnote.
        :param text: text content of the footnote.
        """
        back = (
            '<a href="#fnref-%s" class="footnote">&#8617;</a>'
        ) % escape(key)
        text = text.rstrip()
        if text.endswith('</p>'):
            text = re.sub(r'<\/p>$', r'%s</p>' % back, text)
        else:
            text = '%s<p>%s</p>' % (text, back)
        html = '<li id="fn-%s">%s</li>\n' % (escape(key), text)
        return html

    def footnotes(self, text):
        """Wrapper for all footnotes.

        :param text: contents of all footnotes.
        """
        html = '<div class="footnotes">\n%s<ol>%s</ol>\n</div>\n'
        return html % (self.hrule(), text)
