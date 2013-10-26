from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.views.generic import TemplateView

from hljs_org import views

urlpatterns = patterns('',

    url(r'^$', views.index, name='index'),
    url(r'^download/$', views.download, name='download'),
    url(r'^contribute/$', TemplateView.as_view(template_name='contribute.html'), name='contribute'),

    url(r'^admin/', include(admin.site.urls)),

)
