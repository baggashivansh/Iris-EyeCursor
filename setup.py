from setuptools import setup

APP = ['app/iris.py']  # main script
ICON = 'assets/iris_icon.icns'  # macOS icon

OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5'],
    'iconfile': ICON,
    'plist': {
        'CFBundleName': 'Iris',
        'CFBundleDisplayName': 'Iris',
        'CFBundleIdentifier': 'com.shivansh.iris',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True  # hides dock icon, tray-only app
    },
    'compressed': True,      # smaller app bundle
    'optimize': 2,           # bytecode optimization
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
