from django import template

register = template.Library()

# @register.filter
# def in_list(value, arg):
#     """
#     Usage: {{ value|in_list:"1,2,3" }}
#     Returns True if value is in list
#     """
#     return str(value) in arg.split(',')
@register.filter
def in_list(value, arg):
    try:
        items = [int(x.strip()) for x in arg.split(',')]
        return int(value) in items
    except:
        return False