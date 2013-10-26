import os
import re

def version(path):
    try:
        readme = open(os.path.join(path, 'README.md')).read()
    except FileNotFoundError:
        return ''
    match = re.search(r'Version: ([0-9\.]+)', readme)
    return match and match.group(1) or ''
