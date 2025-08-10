try:
    from setuptools import setup
except:
    from distutils.core import setup

config = {
    'description': 'Tiferet Monday, a Tiferet app for managing Monday.com boards and items.',
    'author': 'Andrew Shatz, Great Strength Systems',
    'url': r'https://github.com/greatstrength/tiferet-monday',
    'download_url': r'https://github.com/greatstrength/tiferet-monday',
    'author_email': 'andrew@greatstrength.me',
    'version': '0.1.0a0',
    'license': 'BSD 3',
    'install_requires': [
        'schematics>=2.1.1',
        'pyyaml>=6.0.1',
        'dependencies>=7.7.0'
    ],
    'packages': [
        'tiferet_monday',
        'tiferet_monday.commands',
        'tiferet_monday.configs',
        'tiferet_monday.contracts',
        'tiferet_monday.proxies',
        'tiferet_monday.proxies.monday',
    ],    
    'scripts': [],
    'name': 'tiferet-monday',
    'extras_require': {
        'test': ['pytest>=8.3.3', 'pytest_env>=1.1.5'],
    }
}

setup(**config)