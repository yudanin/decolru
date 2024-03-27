from django import template

register = template.Library()

@register.filter
def truncate_tags(tags_str):
    tags = tags_str.split(',')
    if len(tags) > 3:
        return ', '.join(tags[:3]) + ' ...'
    else:
        return tags_str