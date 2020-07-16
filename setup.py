try: 
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = [
    'description': 'Python sorting algorithm visualizer using MatPlotLib',
    'author': 'Nicholas Carnival',
    'packages': 'find_packages()',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'projectname'
]

# add curses to dependencies

setup(**config)