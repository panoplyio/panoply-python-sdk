from distutils.core import setup
from panoply import VERSION, PKGNAME
setup(
    name = PKGNAME,
    version = VERSION,
    py_modules = [ "panoply" ]
)