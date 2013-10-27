import os
import sys
import re
from io import BytesIO
import zipfile

import build


def version(path):
    try:
        readme = open(os.path.join(path, 'README.md')).read()
    except FileNotFoundError:
        return ''
    match = re.search(r'Version: ([0-9\.]+)', readme)
    return match and match.group(1) or ''

def counts(path):
    return {
        ftype: len([f for f in os.listdir(os.path.join(path, 'src', ftype)) if f.endswith(extension)])
        for ftype, extension
        in [('languages', '.js'), ('styles', '.css')]
    }

def buildzip(src_path, cache_path, filenames):
    result = BytesIO()
    zip = zipfile.ZipFile(result, 'w')
    for filename in ['README.md', 'README.ru.md', 'classref.txt', 'LICENSE']:
        zip.write(os.path.join(src_path, filename), filename)
    styles_path = os.path.join(src_path, 'src', 'styles')
    for filename in os.listdir(styles_path):
        zip.write(os.path.join(styles_path, filename), 'styles/%s' % filename)
    languages = [os.path.splitext(f)[0] for f in filenames]
    filenames = build.language_filenames(os.path.join(src_path, 'src'), languages)
    filenames = [os.path.join(cache_path, os.path.basename(f)) for f in filenames]
    hljs = build.glue_files(os.path.join(cache_path, 'highlight.js'), filenames, True)
    info = zipfile.ZipInfo('highlight.pack.js')
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
