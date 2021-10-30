from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from wildewidgets import (
    BasicMenu,
    MenuMixin,
)


class MainMenu(BasicMenu):
    items = [('Home', 'core:home')]


class HomeView(MenuMixin, TemplateView):
    template_name = "core/home.html"
    menu_class = MainMenu
    menu_item = "Home"

    def get_context_data(self, **kwargs):
        kwargs['mydata'] = 'Here is my data.'
        return super().get_context_data(**kwargs)
