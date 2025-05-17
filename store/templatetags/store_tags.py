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

@register.filter
def call_with_arg(obj, arg):
    """
    Call a method on an object with the given argument.
    Usage: {{ object|call_with_arg:"method_name:argument" }}
    """
    method_name, arg_value = arg.split(':')
    if hasattr(obj, method_name):
        method = getattr(obj, method_name)
        return method(arg_value)
    return None

@register.simple_tag
def get_matching_rendered_image(rendered_images, color):
    """
    Find the first rendered image that matches the given color.
    Usage: {% get_matching_rendered_image product.rendered_images.all item.color as matching_image %}
    """
    for image in rendered_images:
        if image.color == color:
            return image
    return None
