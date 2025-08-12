from aclib.pyi import compile, pyipack

# compile(
#     srcdir='src',
#     dstdir='compiled',
#     exclude_scripts=['main.py'],
#     dst_replace_confirm=False
# )

pyipack(
    scriptpath='src/main.py',
    distdir='dist',
    dst_replace_confirm=True,
    appname='showtext',
    appversion='',
    appicon='',
    exename='launcher',
    show_console=True,
    admin_permission=True,
    one_file_mode=True,
    appfiles=['assets'],
    modules_which_require_extra_data=['aclib.pywebview'],
)
