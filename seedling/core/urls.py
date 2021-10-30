from django.urls import path

from .views import HomeView

# These URLs are loaded by seedling/urls.py.
app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
