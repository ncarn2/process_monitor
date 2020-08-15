import os
import sys

try: 
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (3, 0):
    print('This application requires at least Python 3.0 to run.')
    sys.exit(1)

dependencies = ['nose', 'psutil']

if os.name == 'nt':
    dependencies.append('windows-curses')

config = {
    'description': 'Python system monitor similar to htop',
    'author': 'Nicholas Carnival',
    'version': '0.1',
    'install_requires': dependencies,
    'scripts': [],
    'name': 'system_monitor'
}

# add curses to dependencies
setup(**config)