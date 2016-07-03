from distutils.core import setup
from panoply import VERSION, PKGNAME
setup(
    name = PKGNAME,
    version = VERSION,
    packages=["panoply"]
)