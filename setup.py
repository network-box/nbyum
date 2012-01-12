import os
import sys

from distutils.core import setup


requires = [
    # Not available from Pypi, but worth mentioning for packagers
    #'yum',
    ]

if sys.version_info < (2, 7):
    requires.append('argparse')


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()


setup(name='nbyum',
      version='0.0.1',
      description='Just like yum, but with a usable output',
      long_description=README,
      author='Mathieu Bridon',
      author_email='mathieu.bridon@network-box.com',
      license='GPLv3+',
      url="https://www.network-box.com",
      package_dir={'': 'src'},
      packages=['nbyum'],
      scripts=['nbyum'],
      requires=requires,
      )
