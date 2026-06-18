from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.filter(name='markdown')
def render_markdown(text):
    if not text:
        return ""

    # Enable common extensions like GitHub-Flavored Markdown tables, codehilite, and fenced code blocks
    md = markdown.Markdown(extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc'
    ])

    html_content = md.convert(text)
    return mark_safe(html_content)