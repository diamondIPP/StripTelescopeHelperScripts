
import re


def svn_version(x):
    svn = x.get('RunInfo', 'svn_rev')
    match = re.search(r'[^0123456789]', svn)
    if match:
        first_index = match.start()
        if first_index > 0:
            svn = int(svn[:first_index])
        else:
            svn = -1
    else:
        try:
            svn = int(svn)
        except:
            svn = -1
    return svn