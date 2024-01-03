from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='labelprinter',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Silvio Tomatis',
      author_email='silvio@gropen.net',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'bobo',
          #'reportlab', # use sudo apt-get install python2.6-reportlab-accel
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
