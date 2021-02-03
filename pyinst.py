import PyInstaller.__main__


PyInstaller.__main__.run([
    'main.py',
    'map.py',
    'menu.py',
    'save.py',
    'settings.py',
    'sprites.py',
    'tools.py',
    '-y',
    '-w',
    '--add-data=data;.\\data'
])
