from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Gets a value from a dictionary by key.
    Used in templates where you need dict[key] but Django templates
    don't support bracket notation for variables.

    Usage: {{ my_dict|get_item:my_key }}
    """
    return dictionary.get(key, 1)