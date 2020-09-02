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


@register.simple_tag
def items_by_date_range(category, begin_date, end_date):
    results = {}
    items = category.item_set.filter(
        pub_date__range=[begin_date, end_date])

    for item in items:
        name = item.item_name
        results[name] = results.get(
            name, 0) + item.duration

    results = {k: v for k, v in sorted(
        results.items(), key=lambda item: item[1], reverse=True)}

    return results
