import os
import logging
import random
import json
import re
import subprocess

from django import http
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, resolve_url
from django.utils.html import mark_safe
from django.core.cache import cache
from django.conf import settings
from pkg_resources import parse_version

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
            'version': version,
            'cdns': list(lib.check_cdns(settings.HLJS_CDNS, version, cache)),
            'commons': commons,
            'others': others,
        })

def usage(request):
    return render(request, 'usage.html', {
        'text': mark_safe(lib.readme(settings.HLJS_SOURCE)),
    })

@csrf_exempt
def release(request):
    if request.method == 'POST':
        data = json.loads(request.read().decode('utf-8'))
        event = request.META.get('HTTP_X_GITHUB_EVENT', 'event')
        if event == 'push':
            match = re.match(r'refs/tags/(\d+(\.\d+)+)', data['ref'])
            version = match.group(1) if match else '-'
        elif event == 'release':
            version = data['release']['tag_name']
        else:
            version = '0'
        if parse_version(version) >= parse_version(lib.version(settings.HLJS_SOURCE)):
            result = 'Started update to version %s. Watch progress at %s.\n' % (
                version,
                request.build_absolute_uri(resolve_url(release)),
            )
            status = 202
            subprocess.Popen(['./manage.py', 'updatehljs', version])
        else:
            result = 'No update started for version %s.\n' % version
            status = 200
        return http.HttpResponse(result, status=status, content_type='text/plain')
    else:
        return render(request, 'updates.html', {
            'updates': models.Update.objects.order_by('-started'),
        })
