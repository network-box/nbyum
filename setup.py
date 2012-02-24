import os
import sys

from distutils.core import setup, Command


install_requires = [
    # Not available from Pypi, but worth mentioning for packagers
    #"yum",
    #"yum-plugin-nuke-newsave",
    ]

if sys.version_info < (2, 7):
    install_requires.append("argparse")


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst")) as f:
    README = f.read()


class TestCommand(Command):
    """A custom distutils command to run unit tests."""
    user_options = []

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        """Run all the unit tests found in the `tests/' folder."""
        # We use unittest2's skip* decorators, and if we don't help Python it will
        # import the older, incompatible unittest module
        try:
            import unittest2
            sys.modules["unittest"] = unittest2
        except ImportError:
            print("We use unittest2 for the unit tests, please install it")
            sys.exit(1)

        tests = unittest2.collector()
        t = unittest2.TextTestRunner(verbosity=self.verbose)
        result = t.run(tests)

        if result.errors or result.failures:
            sys.exit(1)


setup(name="nbyum",
      # Note: This is a pre-release
      version="5.0.0-svn20708",
      description="Just like yum, but with a usable output",
      long_description=README,
      author="Mathieu Bridon",
      author_email="mathieu.bridon@network-box.com",
      license="GPLv3+",
      url="https://www.network-box.com",
      package_dir={"": "src"},
      packages=["nbyum"],
      scripts=["nbyum"],
      requires=install_requires,
      cmdclass={'test': TestCommand},
      )
