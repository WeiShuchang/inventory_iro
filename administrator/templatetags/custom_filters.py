from django import template

register = template.Library()

@register.filter
def get_item(value, key):
    if isinstance(value, dict):  # Check if the value is a dictionary
        return value.get(key, 0)  # Return 0 if the key is not found
    return value  # Return the value as-is if it's not a dictionary