import debug_toolbar
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path


urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls[:2], namespace=admin.site.name)),

]

if settings.ENABLE_DEBUG_TOOLBAR:
    urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns


def handler500(request):
    """
    A 500 error handler which includes ``request`` in the context. It uses the default '500.html' template.

    The request context processors defined in TEMPLATES don't get run when rendering the 500 errror page, which is why
    we have to include 'request' manually.
    """
    context = {
        'request': request
    }
    return TemplateResponse(request, '500.html', context, status=500)
