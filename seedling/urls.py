"""seedling URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views import defaults as default_views
import multitenancy.urls

from .core import urls as core_urls


urlpatterns = [
    # User management
    path("users/", include("seedling.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # This setup assumes that you're making an access.caltech app, which needs the app name as a prefix for all URLs.
    # If that's not true, you can change this to whatever base path you want, including ''.
    path('', include(core_urls, namespace='core')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add the root site interface
urlpatterns += multitenancy.urls.urlpatterns

if settings.DEVELOPMENT:
    # We don't provide this in test/production because we don't want it there
    urlpatterns.append(path(settings.ADMIN_URL, include(admin.site.urls[:2], namespace=admin.site.name)))
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
        path("500/", default_views.server_error),
    ]

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
