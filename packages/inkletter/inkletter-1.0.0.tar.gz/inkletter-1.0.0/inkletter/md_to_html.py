from mjml import mjml2html

from inkletter.md_to_mjml import parse_markdown_to_mjml


def parse_mjml_to_html(mjml_text):
    return mjml2html(mjml_text)


def parse_markdown_to_html(markdown_text):
    return parse_mjml_to_html(parse_markdown_to_mjml(markdown_text))
