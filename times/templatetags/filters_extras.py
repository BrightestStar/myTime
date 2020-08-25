from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def reverse(value):
    return '-'.join(value.split('/')[::-1])


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def summary(dictionary):
    if isinstance(dictionary, dict):
        return sum(dictionary.values())
