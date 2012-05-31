import os
import sys

from distutils.core import setup, Command


install_requires = [
    # -- Those are not available from Pypi, but worth mentioning for packagers
    #"yum",
    #"yum-plugin-nuke-newsave",
    #"yum-plugin-posttrans-triggers",
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
        if os.getuid() != 0:
            print("Unit tests must unfortunately be run as root")
            sys.exit(1)

        import unittest
        import tests

        loader = unittest.TestLoader()
        t = unittest.TextTestRunner(verbosity=self.verbose)
        result = t.run(loader.loadTestsFromModule(tests))

        if result.errors or result.failures:
            sys.exit(1)


setup(name="nbyum",
      version="5.0.0",
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
