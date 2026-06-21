from django import template

register = template.Library()

@register.simple_tag
def id_check(current_user, thread):
    if current_user == thread.first_user:
        return thread.second_user
    return thread.first_user