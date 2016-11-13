# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

import dashboard.views

urlpatterns = \
    [
        url(r'^$', dashboard.views.do_login, name='login'),
        url(r'^logout/$', dashboard.views.do_logout, name='logout'),
        url(r'^home/$', TemplateView.as_view(template_name="home.html"), name='home'),
        url(r'^activity/$', TemplateView.as_view(template_name="activity.html"), name='activity'),

        url(r'^v1/clients$', dashboard.views.client_list),
        url(r'^v1/nodes', dashboard.views.node_list),

        url(r'^admin/', admin.site.urls)
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
