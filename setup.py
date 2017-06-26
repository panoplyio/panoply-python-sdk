from distutils.core import setup
from panoply import VERSION, PKGNAME
setup(
    name=PKGNAME,
    version=VERSION,
    packages=["panoply"],
    install_requires=[
        "requests==2.3.0",
        "oauth2client==4.1.1"
    ],
    url="https://github.com/panoplyio/panoply-python-sdk",
    author="Panoply.io",
    author_email="support@panoply.io"
)
