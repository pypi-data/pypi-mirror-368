# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['fyers_helper']

package_data = \
{'': ['*']}

install_requires = \
['fyers-apiv3>=3.1,<4.0', 'pandas>=2.3,<3.0', 'retry>=0.9.2,<0.10.0']

setup_kwargs = {
    'name': 'fyers-helper',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
