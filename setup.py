"""
simple downloader for saving a whole ElasticSearch-index, just the corresponding type or just a document into a line-delimited JSON-File
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='fancontrol',
      version='0.1.0',
      description='simple fancontrol based on liquidctl using a Corsair Commander XT and a Water Temperature Sensor attached to it',
      url='https://github.com/boerni667/corsair-command-fancontrol',
      author='Bernhard Hering',
      license="Apache 2.0",
      packages=['fancontrol'],
      package_dir={'fancontrol': './'},
      install_requires=[
          'liquidctl>=1.11.0'
      ],
      python_requires=">=3.5.*",
      entry_points={
          "console_scripts": ["fancontrol.py=fancontrol:run"]
          }
      )

