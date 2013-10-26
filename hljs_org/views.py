from django.shortcuts import render
from django.conf import settings

from hljs_org import lib

def index(request):
    return render(request, 'index.html', {
        'version': lib.version(settings.HLJS_SOURCE_DIR),
        'news': [],
    })

def download(request):
    return ''
