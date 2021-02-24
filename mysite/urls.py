# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.urls import path
from form.views import form_render_view, ranking_view, logout_view, login_view, ranking_by, form_students, form_employers, form_digital_knowledge
admin.autodiscover()

urlpatterns = [
    path('en/anketa/', form_render_view),
    path('en/stud/', form_students),
    path('en/emp/', form_employers),
path('en/dig/', form_digital_knowledge),

    # path('en/ranking/', ranking_view),
    path('logout/', logout_view),
path('en/login/', login_view),
    path('', include("django.contrib.auth.urls")),
    path('en/ranking/', ranking_by),

    # url(r'^en/?ranking=(?P<param>\w+)/$', ranking_by),
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}})
]

urlpatterns += i18n_patterns(
# url(r'^anketa/$','form.views.form_render_view'),
    url(r'^admin/', admin.site.urls),  # NOQA
    url(r'^', include('cms.urls')),
)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
