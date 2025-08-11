import mistune

from inkletter.ast import *
from inkletter.scope import ScopeStack
from inkletter.visitors.annotation import Annotation
from inkletter.visitors.merger import BlockTextMerger


class ASTRenderer(mistune.BaseRenderer):
    def render_token(self, token, state):
        func = self._get_method(token["type"])
        attrs = token.get("attrs")

        if "raw" in token:
            text = token["raw"]
        elif "children" in token:
            text = self.render_tokens(token["children"], state)
        else:
            text = None

        if attrs:
            if text is not None:
                return func(text, **attrs)
            return func(**attrs)
        else:
            if text is not None:
                return func(text)
            return func()

    def render_tokens(self, tokens, state):
        nodes = []
        for token in tokens:
            rv = self.render_token(token, state)
            if rv is None:
                continue
            if isinstance(rv, list):
                nodes.extend(rv)
            else:
                nodes.append(rv)
        return nodes

    def __call__(self, tokens, state):
        return Document(self.render_tokens(tokens, state))

    # --- Inline renderers ---

    def text(self, value):
        return LiteralText(value)

    def emphasis(self, text):
        return Emphasis(text)

    def strong(self, text):
        return Strong(text)

    def strikethrough(self, text):
        return StrikeThrough(text)

    def codespan(self, text):
        return CodeSpan(text)

    def link(self, text, url, title=None):
        # If the text contains an image, we create an ImageLink
        # We extract the image from the text to create a new ImageLink node
        # The rest of the text is ignored
        if img := next((t for t in text if isinstance(t, Image)), None):
            return ImageLink(img, url, title)
        else:
            return Link(text, url, title)

    # --- Block renderers ---

    def paragraph(self, text):
        return Paragraph(text)

    def heading(self, text, level):
        return Heading(level, text)

    def block_code(self, code, info=None):
        language = info.strip() if info else None
        return BlockCode(code, language)

    def block_text(self, text):
        return BlockText(text)

    def thematic_break(self):
        return ThematicBreak()

    def blank_line(self):
        return BlankLine()

    def linebreak(self):
        return LineBreak()

    def softbreak(self):
        return SoftBreak()

    def block_quote(self, text):
        return BlockQuote(text)

    def image(self, alt, url, title=None):
        if alt:
            # The tokenizer return always a list of a single text
            assert isinstance(alt, list), alt
            assert len(alt) == 1, alt
            alt = alt[0]
        return Image(url, alt, title)

    # --- List renderers ---

    def list(self, elements, ordered, **attrs):
        return List(elements, ordered=ordered)

    def list_item(self, element, **attrs):
        return ListItem(element)

    # --- Task renderers ---

    def task_list_item(self, text, checked=False):
        return TaskListItem(text, checked)

    # --- Table renderers ---

    def table(self, children):
        header = next(filter(lambda c: isinstance(c, TableHeader), children))
        rows = list(filter(lambda c: isinstance(c, TableRow), children))
        return Table(header=header, rows=rows)

    def table_body(self, text):
        return text

    def table_head(self, text):
        return TableHeader(text)

    def table_row(self, content):
        return TableRow(content)

    def table_cell(self, text, align=None, head=False):
        if head:
            return TableHeaderCell(text, align=align)
        else:
            return TableCell(text, align=align)


def parse_markdown_to_ast(markdown_text):
    renderer = ASTRenderer()
    markdown = mistune.create_markdown(
        renderer=renderer,
        plugins=[
            "mistune.plugins.formatting.strikethrough",
            "mistune.plugins.table.table",
            "mistune.plugins.table.table_in_list",
            "mistune.plugins.table.table_in_quote",
            "mistune.plugins.task_lists.task_lists",
        ],
    )
    ast = markdown(markdown_text)
    BlockTextMerger().visit(ast, scope=None)
    Annotation().visit(ast, scope=ScopeStack())
    return ast
