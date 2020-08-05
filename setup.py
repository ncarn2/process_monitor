try: 
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Python process monitor similar to htop',
    'author': 'Nicholas Carnival',
    'version': '0.1',
    'install_requires': ['nose', 'psutil'],
    'scripts': [],
    'name': 'process_monitor'
}

# add curses to dependencies
setup(**config)
