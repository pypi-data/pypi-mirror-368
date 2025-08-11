from inkletter.codeblock import CodeBlock, codeblock_from_string, CodeBlockResolver
from inkletter.md_to_ast import parse_markdown_to_ast
from inkletter.visitors.codegen import Codegen
from inkletter.visitors.tree import print_tree


def parse_markdown_to_mjml(markdown_text, print_ast=True, use_style=False):
    ast = parse_markdown_to_ast(markdown_text)
    if print_ast:
        print_tree(ast)
    codegen = Codegen(use_style=use_style)
    codegen.visit(ast, scope=None)
    code = codegen.get_code()
    return code


def wrap_mjml_body(content):
    if isinstance(content, str):
        content = codeblock_from_string(content)

    root = CodeBlock()
    root.add_text("<mjml>")
    root.add_newline()
    root.add_indent()

    root.add_text("<mj-body>")
    root.add_newline()
    root.add_indent()

    root.add_text("<mj-section>")
    root.add_newline()
    root.add_indent()

    root.add_text("<mj-column>")
    root.add_newline()
    root.add_indent()

    root.add_codeblock(content)

    root.add_dedent()
    root.add_text("</mj-column>")
    root.add_newline()

    root.add_dedent()
    root.add_text("</mj-section>")
    root.add_newline()

    root.add_dedent()
    root.add_text("</mj-body>")
    root.add_newline()

    root.add_dedent()
    root.add_text("</mjml>")
    root.add_newline()

    resolver = CodeBlockResolver()
    return resolver.resolve(root)
