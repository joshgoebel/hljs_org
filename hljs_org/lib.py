import os
import sys
import re
from io import BytesIO
import zipfile
from datetime import datetime
from urllib import request
from codecs import open

from django.utils.html import escape
import markdown

import build


def version(path):
    try:
        readme = open(os.path.join(path, 'CHANGES.md'), encoding='utf-8').read()
    except FileNotFoundError:
        return ''
    match = re.search(r'^## Version ([0-9\.]+)', readme, re.M)
    return match and match.group(1) or ''

def news(path, version):
    try:
        readme = open(os.path.join(path, 'CHANGES.md'), encoding='utf-8').read()
    except FileNotFoundError:
        return ''
    match = re.search(r'^## Version (%s).*?\n+' % re.escape(version), readme, re.M)
    if not match:
        return ''
    header = readme[match.start() + 3:match.end()]
    readme = readme[match.end():]
    match = re.search(r'^## ', readme, re.M)
    if match:
        readme = readme[:match.start()]
    return header + readme.strip()

def check_cdn(url):
    try:
        status = request.urlopen(url).status
    except request.HTTPError as e:
        status = e.code
    return url if status == 200 else None

def check_cdns(cdn_templates, version, cache=None):
    for title, script_url, style_url in cdn_templates:
        script_url = script_url % version
        style_url = style_url % version
        script_url = cache.get(script_url) if cache else check_cdn(script_url, version)
        if script_url:
            yield title, script_url, style_url

def counts(path):
    return {
        ftype: len([f for f in os.listdir(os.path.join(path, 'src', ftype)) if f.endswith(extension)])
        for ftype, extension
        in [('languages', '.js'), ('styles', '.css')]
    }

def buildzip(src_path, cache_path, filenames):
    result = BytesIO()
    zip = zipfile.ZipFile(result, 'w')
    for filename in ['README.md', 'README.ru.md', 'CHANGES.md', 'LICENSE']:
        zip.write(os.path.join(src_path, filename), filename)
    styles_path = os.path.join(src_path, 'src', 'styles')
    for filename in os.listdir(styles_path):
        zip.write(os.path.join(styles_path, filename), 'styles/%s' % filename)
    languages = [os.path.splitext(f)[0] for f in filenames]
    filenames = build.language_filenames(os.path.join(src_path, 'src'), languages)
    filenames = [os.path.join(cache_path, os.path.basename(f)) for f in filenames]
    hljs = build.glue_files(os.path.join(cache_path, 'highlight.js'), filenames, True)
    info = zipfile.ZipInfo('highlight.pack.js', date_time=datetime.now().timetuple()[:6])
    info.external_attr = 0o644 << 16
    zip.writestr(info, hljs)
    zip.close()
    result.seek(0)
    return result

def listlanguages(src_path):
    lang_path = os.path.join(src_path, 'src', 'languages')
    filenames = os.listdir(lang_path)
    languages = [(build.parse_header(os.path.join(lang_path, f)), f) for f in filenames]
    languages.sort(key=lambda l: l[0]['Language'])

    def is_common(f):
        return os.path.splitext(f)[0] in build.CATEGORIES['common']

    commons = [(i, f) for i, f in languages if is_common(f)]
    others = [(i, f) for i, f in languages if not is_common(f)]
    return commons, others

def readme(path):
    try:
        readme = open(os.path.join(path, 'README.md'), encoding='utf-8').read()
    except FileNotFoundError:
        return ''
    try:
        readme = readme[readme.find('## Getting Started'):]
    except IndexError:
        pass

    def replace_code(match):
        code = escape(match.group(2))
        language = match.group(1)
        return '<pre><code class="%s">%s</code></pre>' % (language, code)

    readme = re.sub(r'^```(\w+)\n(.*?)\n```\n', replace_code, readme, flags=re.M | re.S)
    return markdown.markdown(readme, safe_mode=False)
