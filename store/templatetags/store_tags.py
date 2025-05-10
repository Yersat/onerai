from django import template

register = template.Library()

@register.filter
def split_tags(value, delimiter=','):
    """
    Split a string by delimiter and return a list of strings.
    Usage: {{ value|split_tags:"," }}
    """
    if not value:
        return []
    return [tag.strip() for tag in value.split(delimiter)]
