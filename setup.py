import glob
import os
import unittest
import sys

from distutils.core import setup, Command


requires = [
    # Not available from Pypi, but worth mentioning for packagers
    #"yum",
    ]

if sys.version_info < (2, 7):
    requires.append("argparse")


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst")) as f:
    README = f.read()


class TestCommand(Command):
    description = "Run the unit tests for the module"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def __get_testfiles(self):
        for t in glob.iglob(os.path.join("tests", "*.py")):
            basename = os.path.basename(t)

            if basename != "__init__.py__":
                yield "tests.%s" % os.path.splitext(basename)[0]

    def run(self):
        testfiles = []

        tests = unittest.TestLoader().loadTestsFromNames(self.__get_testfiles())
        t = unittest.TextTestRunner(verbosity=1)
        t.run(tests)


setup(name="nbyum",
      version="0.0.1",
      description="Just like yum, but with a usable output",
      long_description=README,
      author="Mathieu Bridon",
      author_email="mathieu.bridon@network-box.com",
      license="GPLv3+",
      url="https://www.network-box.com",
      package_dir={"": "src"},
      packages=["nbyum"],
      scripts=["nbyum"],
      requires=requires,
      cmdclass={'test': TestCommand},
      )
