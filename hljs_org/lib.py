import os
import sys
import re
from io import BytesIO
import zipfile
from datetime import datetime
from urllib import request, parse
import logging

from django.utils.html import escape
import markdown


log = logging.getLogger('hljs_org.lib')


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

def snippet(path, language):
    try:
        filename = os.path.join(path, 'test', 'detect', language, 'default.txt')
        return open(filename, encoding='utf-8').read()
    except FileNotFoundError:
        return ''

def check_cdn(url):
    try:
        status = request.urlopen(parse.urljoin('http:', url)).status
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

def parse_header(filename):
    content = open(filename, encoding='utf-8').read(1024)
    match = re.search(r'^\s*/\*(.*?)\*/', content, re.S)
    if not match:
        return
    try:
        headers = match.group(1).split('\n')
        headers = dict(h.strip().split(': ', 1) for h in headers if ': ' in h)
        for key in ['Requires', 'Category']:
            headers[key] = [v.strip() for v in headers.get(key, '').split(',') if v]
    except Exception as e:
        log.error('Error parsing header of %s: %s' % (filename, e))
        raise
    return headers if 'Language' in headers else None

def _with_dependents(path, names):
    for name in names:
        filename = os.path.join(path, name)
        header = os.path.exists(filename) and parse_header(filename)
        if header:
            yield from _with_dependents(path, header['Requires'])
            yield name

def _dedupe(sequence):
    seen = set()
    for item in sequence:
        if item not in seen:
            yield item
        seen.add(item)

def buildzip(src_path, cache_path, filenames):
    result = BytesIO()
    zip = zipfile.ZipFile(result, 'w')
    for filename in ['README.md', 'README.ru.md', 'CHANGES.md', 'LICENSE']:
        zip.write(os.path.join(src_path, filename), filename)
    styles_path = os.path.join(src_path, 'src', 'styles')
    for filename in os.listdir(styles_path):
        zip.write(os.path.join(styles_path, filename), 'styles/%s' % filename)
    languages = list(_dedupe(_with_dependents(os.path.join(src_path, 'src', 'languages'), filenames)))
    filenames = [os.path.join(cache_path, 'languages', l.replace('.js', '.min.js')) for l in languages]
    hljs = ''.join(
        open(f, encoding='utf-8').read()
        for f in [os.path.join(cache_path, 'highlight.min.js')] + filenames
    )
    info = zipfile.ZipInfo('highlight.pack.js', date_time=datetime.now().timetuple()[:6])
    info.external_attr = 0o644 << 16
    zip.writestr(info, hljs)
    zip.close()
    result.seek(0)
    return result, languages

def listlanguages(src_path):
    lang_path = os.path.join(src_path, 'src', 'languages')
    filenames = os.listdir(lang_path)
    languages = [(parse_header(os.path.join(lang_path, f)), f) for f in filenames]
    languages.sort(key=lambda l: l[0]['Language'])
    commons = [(h, f) for h, f in languages if 'common' in h['Category']]
    others = [(h, f) for h, f in languages if 'common' not in h['Category']]
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
