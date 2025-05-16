from django import template
from decimal import Decimal

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

@register.filter
def multiply(value, arg):
    """
    Multiply the value by the argument.
    Usage: {{ value|multiply:arg }}
    """
    try:
        # Convert to Decimal for precise decimal arithmetic
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0
