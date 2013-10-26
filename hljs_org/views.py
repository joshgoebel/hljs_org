import os
import sys
from io import BytesIO
import zipfile
import logging

from django import http
from django.shortcuts import render
from django.conf import settings

from hljs_org import lib
sys.path.insert(0, os.path.join(settings.HLJS_SOURCE_DIR, 'tools'))
import build

log = logging.getLogger('hljs_download')

def index(request):
    return render(request, 'index.html', {
        'version': lib.version(settings.HLJS_SOURCE_DIR),
        'news': [],
    })

def download(request):
    if request.method == 'POST':
        buffer = BytesIO()
        zip = zipfile.ZipFile(buffer, 'w')
        for filename in ['README.md', 'README.ru.md', 'classref.txt', 'LICENSE']:
            zip.write(os.path.join(settings.HLJS_SOURCE_DIR, filename),filename)
        styles_path = os.path.join(settings.HLJS_SOURCE_DIR, 'src', 'styles')
        for filename in os.listdir(styles_path):
            zip.write(os.path.join(styles_path, filename), 'styles/%s' % filename)
        languages = [os.path.splitext(f)[0] for f in request.POST.keys()]
        filenames = build.language_filenames(os.path.join(settings.HLJS_SOURCE_DIR, 'src'), languages)
        filenames = [os.path.join(settings.HLJS_CACHE, os.path.basename(f)) for f in filenames]
        hljs = build.glue_files(os.path.join(settings.HLJS_CACHE, 'highlight.js'), filenames, True)
        info = zipfile.ZipInfo('highlight.pack.js')
        info.external_attr = 0o644 << 16
        zip.writestr(info, hljs)
        zip.close()
        buffer.seek(0)
        log.info(' '.join(sorted(request.POST.keys())))
        response = http.HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=highlight.zip'
        return response
    else:
        lang_path = os.path.join(settings.HLJS_SOURCE_DIR, 'src', 'languages')
        filenames = os.listdir(lang_path)
        languages = [(build.parse_header(os.path.join(lang_path, f)), f) for f in filenames]
        languages.sort(key=lambda l: l[0]['Language'])

        def is_common(f):
            return os.path.splitext(f)[0] in build.CATEGORIES['common']

        commons = [(i, f) for i, f in languages if is_common(f)]
        others = [(i, f) for i, f in languages if not is_common(f)]
        return render(request, 'download.html', {
            'commons': commons,
            'others': others,
        })
