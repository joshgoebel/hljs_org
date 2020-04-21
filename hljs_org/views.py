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
releaselog = logging.getLogger('hljs_orgi.release')

def curnext(items, index):
    if index is None:
        index = random.randrange(0, len(items))
    try:
        index = int(index)
        items[index]
    except (ValueError, IndexError):
        raise http.Http404
    return index, (index + 1) % len(items)

def index(request):
    snippets = [lib.snippet(settings.HLJS_SOURCE, l) for l in settings.HLJS_SNIPPETS]
    snippet_current, snippet_next = curnext(snippets, request.GET.get('snippet'))
    styles = settings.HLJS_CODESTYLES
    style_current, style_next = curnext(styles, request.GET.get('style'))
    template_name = 'snippet.html' if request.is_ajax() else 'index.html'
    return render(request, template_name, {
        'version': lib.version(settings.HLJS_SOURCE),
        'counts': lib.counts(settings.HLJS_SOURCE),
        'snippet': snippets[snippet_current],
        'snippet_current': snippet_current,
        'snippet_next': snippet_next,
        'styles': styles,
        'style': styles[style_current],
        'style_current': style_current,
        'style_next': style_next,
        'news': models.News.objects.order_by('-created')[:10],
    })

def download(request):
    if request.method == 'POST':
        languages = set(request.POST.keys())
        content, languages = lib.buildzip(settings.HLJS_SOURCE, settings.HLJS_CACHE, languages)
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
        releaselog.info('Github event: %s' % event)
        if event == 'push':
            match = re.match(r'refs/tags/(.*)', data['ref'])
            version = match.group(1) if match else '0'
        elif event == 'release':
            version = data['release']['tag_name']
        else:
            version = '0'
        version = parse_version(version)
        current_version = parse_version(lib.version(settings.HLJS_SOURCE))
        releaselog.info('Parsed version: %s, current version: %s' % (version, current_version))
        if not version.is_prerelease and version >= current_version:
            result = 'Started update to version %s. Watch progress at %s.\n' % (
                version,
                request.build_absolute_uri(resolve_url(release)),
            )
            status = 202
            subprocess.Popen(['venv/bin/python', 'manage.py', 'updatehljs', str(version)])
        else:
            result = 'No update started for version %s.\n' % version
            status = 200
        return http.HttpResponse(result, status=status, content_type='text/plain')
    else:
        return render(request, 'updates.html', {
            'updates': models.Update.objects.order_by('-started'),
        })
