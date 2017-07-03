from distutils.core import setup

execfile('panoply/constants.py')


setup(
    name=__package_name__,
    version=__version__,
    packages=["panoply"],
    install_requires=[
        "requests==2.3.0",
        "oauth2client==4.1.1"
    ],
    extras_require={
        "test": [
            "pep8==1.7.0",
            "coverage==4.3.4"
        ]
    },
    url="https://github.com/panoplyio/panoply-python-sdk",
    author="Panoply.io",
    author_email="support@panoply.io"
)
