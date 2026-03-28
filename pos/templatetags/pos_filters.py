from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    return value.split(delimiter)

@register.filter
def currency(value):
    try:
        return f"Rp {int(float(value)):,}".replace(',', '.')
    except (ValueError, TypeError):
        return value
