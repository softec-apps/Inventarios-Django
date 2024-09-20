from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Divide la cadena usando el delimitador especificado"""
    return value.split(arg)