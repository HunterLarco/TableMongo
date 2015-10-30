# Always prefer setuptools over distutils
from setuptools import setup, find_packages


setup(
  name='TableMongo',
  version='1.0.1',
  description='TableMongo. A MongoDB ORM based on Google\'s BigTable Syntax',
  url='https://github.com/HunterLarco/TableMongo',
  author='Hunter John Larco',
  author_email='hunter@larcolabs.com',
  license='MIT',
  
  # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
  classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 2 - Pre-Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
  ],
  
  # What does your project relate to?
  keywords='mongodb tablemongo table mongo db database storage orm',

  packages=[
    "TableMongo",
  ],

  # List run-time dependencies here.  These will be installed by pip when
  # your project is installed. For an analysis of "install_requires" vs pip's
  # requirements files see:
  # https://packaging.python.org/en/latest/requirements.html
  install_requires=['pymongo', 'flask']
)