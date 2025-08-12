from __future__ import annotations

import os, glob, re, platform, tempfile
from distutils.dir_util import remove_tree, copy_tree

from .const import DIR_COMPILED
from .colorstr import *

__all__ = ['compile']

def matchpath(*globexps: str, root='', onlyfile=False, onlydir=False) -> list[str]:
    if onlyfile and onlydir: raise TypeError(
        'can not set onlyfile and onlydir at the same time')
    paths = set()
    for expression in globexps:
        paths.update(glob.glob(os.path.join(root, expression), recursive=True))
    if onlyfile:
        paths = filter(lambda fp: os.path.isfile(fp), paths)
    if onlydir:
        paths = filter(lambda fp: os.path.isdir(fp), paths)
    return sorted(map(lambda p: os.path.join(root, os.path.relpath(p, root)), paths))

def unicodeOf(string: str) -> str:
    return ''.join(char.encode('unicode-escape').decode() if ord(char) > 256 else char for char in string)

def unicode_stringcode(stringcode_match: re.Match):
    stringcode = stringcode_match.group(0)
    if not stringcode.startswith('f'):
        return unicodeOf(stringcode)
    fstring = stringcode
    # 查找f-string中的expression part
    breakpoints = [0]
    start = end = brackCount = 0
    for i,char in enumerate(fstring):
        if char == '{':
            brackCount += 1
            if brackCount==1: start=i
            if brackCount==2 and fstring[i-1] == '{': brackCount=0
        if char == '}':
            if brackCount==1:
                end=i+1
                breakpoints += [start, end]
            if brackCount!=0: brackCount -= 1
    breakpoints.append(len(fstring))

    newstr = ''
    for i in range(0, len(breakpoints), 2):
        fir, sec = breakpoints[i], breakpoints[i+1]
        newstr += unicodeOf(fstring[fir:sec])
        if i+2<len(breakpoints): newstr += fstring[sec:breakpoints[i+2]]
    return newstr

def compile(srcdir: str, dstdir: str = DIR_COMPILED, exclude_scripts: list[str] = None, dst_replace_confirm=True) -> str:
    """exclude_scripts is a list of glob expressions whose root equals srcdir."""

    dstdir = dstdir or 'compiled'
    exclude_scripts = exclude_scripts or []
    language_level = platform.python_version().split(".")[0]
    stringcode_pattern = 'f?((["\']{3})|(["\']))[\\s\\S]*?(?<!\\\\)\\1|#[\\s\\S]+?(?=\n|$)'
    with tempfile.TemporaryDirectory(dir='') as tempdir:
        copy_tree(srcdir, tempdir)
        all_pyfiles = matchpath('**/*.py', root=tempdir, onlyfile=True)
        exclude_pyfiles = matchpath(*exclude_scripts, root=tempdir, onlyfile=True)
        compiling_pyfiles = sorted(set(all_pyfiles) - set(exclude_pyfiles))
        builddir_content1 = matchpath('build', 'build/*', root=tempdir, onlydir=True)

        for pyfile in compiling_pyfiles:
            print(redstr(f'\nCompiling script {os.path.abspath(pyfile.replace(tempdir, srcdir, 1))} {"-"*30}> '))
            with open(pyfile, 'r', encoding='utf8') as f:
                srccode = f.read()
            with open(pyfile, 'w', encoding='utf8') as f:
                f.write(re.sub(stringcode_pattern, unicode_stringcode, srccode))
            for i in range(3):
                extcode = os.system(f'cythonize -i -{language_level} {pyfile}')
                if extcode == 0: break
            if extcode != 0:
                print(redstr(f'Compile failed: {os.path.abspath(pyfile.replace(tempdir, srcdir, 1))}'))
                raise SystemExit(extcode)
            os.remove(pyfile)
            os.remove(pyfile[0:-2] + 'c')
        builddir_content2 = matchpath('build', 'build/*', root=tempdir, onlydir=True)
        for buildlib in set(builddir_content2) - set(builddir_content1):
            if os.path.exists(buildlib):
                remove_tree(buildlib)
        for pydfile in matchpath('**/*.cp*.pyd', root=tempdir, onlyfile=True):
            pydparts = pydfile.split('.')
            pydparts.pop(-2)
            os.rename(pydfile, '.'.join(pydparts))

        if os.path.exists(dstdir):
            if dst_replace_confirm:
                reply = input(yellowstr(f'Distdir "{os.path.abspath(dstdir)}" exists, it will be replaced, continue?(y/n): '))
                if reply != 'y':
                    return print('compile canceled') or ''
            remove_tree(dstdir)
        copy_tree(tempdir, dstdir)
        print(greenstr(f'Compiled project: {os.path.abspath(dstdir)}'))
        return dstdir
