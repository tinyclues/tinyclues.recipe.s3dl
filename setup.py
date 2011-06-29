import os
from setuptools import setup, find_packages

version = '0.1'

name = 'tinyclues.recipe.s3dl'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name=name,
      version=version,
      description="ZC Buildout recipe to download files from S3 buckets",
      long_description=read('tinyclues','recipe','s3dl','README.rst'),
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Buildout",
          ],
      keywords='buildout, zc.buildout, recipe, s3',
      author='Olivier Hervieu',
      author_email='olivier.hervieu@tinyclues.com',
      url='https://github.com/',
      license='',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tinyclues.recipe','tinyclues'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'distribute',
          'zc.buildout',
          'boto',
      ],
      extras_require={
        'test' : ['zope.testing'],
      },
      tests_require = ['zope.testing'],
      test_suite = '%s.tests.test_suite' % name,
      entry_points = { 'zc.buildout' : ['default = tinyclues.recipe.s3dl:Recipe'] },
      )
