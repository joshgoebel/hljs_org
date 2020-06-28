from django.urls import path
from django.contrib import admin
from django.views.generic import TemplateView

from hljs_org import views


urlpatterns = [

    path(r'', views.index, name='index'),
    path(r'download/', views.download, name='download'),
    path(r'contribute/', TemplateView.as_view(template_name='contribute.html'), name='contribute'),
    path(r'usage/', views.usage, name='usage'),

    path(r'api/release/', views.release, name='release'),

    path(r'admin/', admin.site.urls),

]
