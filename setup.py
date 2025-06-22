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
    packages=["panoply", "panoply.errors"],
    install_requires=[
        "requests==2.32.3",
        "oauth2client==4.1.1",
        "backoff==1.10.0",
        "sshtunnel==0.1.5",
        "paramiko==3.5.1",
    ],
    extras_require={
        "test": [
            "pycodestyle==2.4.0",
            "coverage==4.5.1",
        ],
    },
    url="https://github.com/panoplyio/panoply-python-sdk",
    author="Panoply.io",
    author_email="support@panoply.io",
)
