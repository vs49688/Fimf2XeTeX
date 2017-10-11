#!/usr/bin/env python

from setuptools import setup, find_packages
from fimf2xetex import __version__

setup(name='fimf2xetex',
	version=__version__,
	packages=['fimf2xetex'],
	install_requires=[
		'beautifulsoup4 ==4.6.0',
		'html5lib ==1.0b10'
	],
	entry_points={
		'console_scripts': [
			'fimf2xetex = fimf2xetex:main'
		]
	}
)
