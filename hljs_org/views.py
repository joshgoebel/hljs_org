import os
import logging

from django import http
from django.shortcuts import render
from django.conf import settings

from hljs_org import lib, models


log = logging.getLogger('hljs_download')


def index(request):
    return render(request, 'index.html', {
        'version': lib.version(settings.HLJS_SOURCE),
        'snippet': models.Snippet.objects.order_by('?')[0],
        'news': [],
    })

def download(request):
    if request.method == 'POST':
        content = lib.buildzip(settings.HLJS_SOURCE, settings.HLJS_CACHE, request.POST.keys())
        log.info(' '.join(sorted(request.POST.keys())))
        response = http.HttpResponse(content, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=highlight.zip'
        return response
    else:
        commons, others = lib.listlanguages(settings.HLJS_SOURCE)
        return render(request, 'download.html', {
            'commons': commons,
            'others': others,
        })
