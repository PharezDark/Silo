from django import template
import markdown
import bleach

register = template.Library()


@register.filter(name='render_markdown')
def render_markdown(text):
    if not text:
        return ""

    # Convert safe markdown blocks to HTML extensions
    html = markdown.markdown(text, extensions=['fenced_code', 'codehilite', 'tables'])

    # Whitelist harmless layout tags, block tracking scripts completely
    allowed_tags = [
        'p', 'b', 'i', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'code', 'pre',
        'ul', 'ol', 'li', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]
    allowed_attrs = {
        'code': ['class'],
        'pre': ['class'],
    }

    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)