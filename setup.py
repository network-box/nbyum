import os
import sys

from setuptools import setup

if sys.argv[1] == "test":
    # We use unittest2's skip* decorators, and if we don't help Python it will
    # import the older, incompatible unittest module
    import unittest2
    sys.modules["unittest"] = unittest2


install_requires = [
    # Not available from Pypi, but worth mentioning for packagers
    #"yum",
    ]

if sys.version_info < (2, 7):
    install_requires.append("argparse")


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst")) as f:
    README = f.read()


setup(name="nbyum",
      # Note: This is a pre-release
      version="5.0.0-svn20453",
      description="Just like yum, but with a usable output",
      long_description=README,
      author="Mathieu Bridon",
      author_email="mathieu.bridon@network-box.com",
      license="GPLv3+",
      url="https://www.network-box.com",
      package_dir={"": "src"},
      packages=["nbyum"],
      scripts=["nbyum"],
      install_requires=install_requires,
      tests_require=["unittest2"],
      test_suite="unittest2.collector",
      )
