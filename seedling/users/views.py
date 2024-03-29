#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(
    LoginRequiredMixin,
    DetailView
):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


class UserListView(
    LoginRequiredMixin,
    ListView
):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


class UserUpdateView(
    LoginRequiredMixin,
    UpdateView
):

    model = User
    fields = ["full_name"]

    def get_success_url(self):
        return reverse("users:user--detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


class UserRedirectView(
    LoginRequiredMixin,
    RedirectView
):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:user--detail", kwargs={"username": self.request.user.username})
