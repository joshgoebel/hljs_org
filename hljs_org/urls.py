from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from hljs_org import views


admin.autodiscover()

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^download/$', views.download, name='download'),
    url(r'^contribute/$', TemplateView.as_view(template_name='contribute.html'), name='contribute'),
    url(r'^usage/$', views.usage, name='usage'),

    url(r'^api/release/$', views.release, name='release'),

    url(r'^admin/', include(admin.site.urls)),

]
