"""blog_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from blogs.views import (UserListView, BlogView, PostCreateView,
                         SubscriptionCreateView, SubscriptionDeleteView,
                         PostView, FeedView, PostReadCreateView)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', UserListView.as_view(), name='index'),

    url(r'^blog/(?P<user_id>[1-9][0-9]*)$', BlogView.as_view(), name='blog'),
    url(r'^blog/(?P<user_id>[1-9][0-9]*)/subscribe$',
        SubscriptionCreateView.as_view(), name='blog_subscribe'),
    url(r'^blog/(?P<pk>[1-9][0-9]*)/unsubscribe$',
        SubscriptionDeleteView.as_view(), name='blog_unsubscribe'),

    url(r'^post/(?P<pk>[1-9][0-9]*)$', PostView.as_view(), name='post'),
    url(r'^post/(?P<pk>[1-9][0-9]*)/read$', PostReadCreateView.as_view(),
        name='post_read'),
    url(r'^post/add$', PostCreateView.as_view(), name='post_add'),

    url(r'^feed$', FeedView.as_view(), name='feed'),

    url(r'^login$', 'django.contrib.auth.views.login',
        {"template_name" : "login.html"}, name="login"),
    url(r'^logout$', 'django.contrib.auth.views.logout',
        {"next_page" : reverse_lazy('login')}, name="logout")
]
