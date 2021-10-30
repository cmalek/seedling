#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import path

from seedling.users.views import (
    UserListView,
    UserRedirectView,
    UserUpdateView,
    UserDetailView,
)

app_name = "users"
urlpatterns = [
    path("", view=UserListView.as_view(), name="users--list"),
    path("~redirect/", view=UserRedirectView.as_view(), name="user--redirect"),
    path("~update/", view=UserUpdateView.as_view(), name="user--update"),
    path("<str:username>/", view=UserDetailView.as_view(), name="user--detail"),
]
