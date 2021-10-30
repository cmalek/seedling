from django import template
from django.urls import reverse


register = template.Library()


@register.inclusion_tag('core/_breadcrumb.html')
def breadcrumb(title, *args, **kwargs):
    """
    Returns bootstrap compatible breadrumb.
    """
    url_name = None
    if args:
        url_name = args[0]
        if len(args) == 1:
            url_args = []
        else:
            url_args = args[1:]
    return {
        'title': title,
        'url': reverse(url_name, *url_args, **kwargs) if url_name else None
    }


@register.inclusion_tag('core/_main_menu.html')
def main_menu(active):
    """
    Returns main menu with the proper tab marked as active.
    """
    return {"active": active}
