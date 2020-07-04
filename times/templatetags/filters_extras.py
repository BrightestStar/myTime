from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def reverse(value):
    return '-'.join(value.split('/')[::-1])
