import os
import logging
import random

from django import http
from django.shortcuts import render
from django.utils.html import mark_safe
from django.conf import settings

from hljs_org import lib, models


downloadlog = logging.getLogger('hljs_org.download')


def index(request):
    return render(request, 'index.html', {
        'version': lib.version(settings.HLJS_SOURCE),
        'counts': lib.counts(settings.HLJS_SOURCE),
        'snippet': models.Snippet.objects.order_by('?').first(),
        'codestyle': 'styles/%s.css' % random.choice(settings.HLJS_CODESTYLES),
        'news': models.News.objects.order_by('-created')[:10],
    })

def download(request):
    if request.method == 'POST':
        languages = set(request.POST.keys())
        languages.remove('csrfmiddlewaretoken')
        content = lib.buildzip(settings.HLJS_SOURCE, settings.HLJS_CACHE, languages)
        downloadlog.info(' '.join(sorted(languages)))
        response = http.HttpResponse(content, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=highlight.zip'
        return response
    else:
        commons, others = lib.listlanguages(settings.HLJS_SOURCE)
        version = lib.version(settings.HLJS_SOURCE)
        return render(request, 'download.html', {
            'cdns': list(lib.check_cdns(settings.HLJS_CDNS, version)),
            'commons': commons,
            'others': others,
        })

def usage(request):
    return render(request, 'usage.html', {
        'text': mark_safe(lib.readme(settings.HLJS_SOURCE)),
    })
