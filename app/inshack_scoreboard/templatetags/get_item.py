from django import template
register = template.Library()


@register.filter('get_item')
def get_item(dictionary, key):
    return dictionary.get(key)
