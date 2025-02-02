#custom_filters.py
from django import template

register = template.Library()

@register.filter
def sum_participacion(values):
    return sum(item['participacion'] for item in values)