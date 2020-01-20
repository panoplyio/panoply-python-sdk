try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

exec(
    compile(
        open('panoply/constants.py', "rb").read(),
        'panoply/constants.py',
        'exec'
    )
)


setup(
    name=__package_name__,
    version=__version__,
    packages=["panoply"],
    install_requires=[
        "requests==2.21.0",
        "oauth2client==4.1.1"
    ],
    extras_require={
        "test": [
            "pep8==2.3.1",
            "python3-coverage==4.5"
        ]
    },
    url="https://github.com/panoplyio/panoply-python-sdk",
    author="Panoply.io",
    author_email="support@panoply.io"
)
