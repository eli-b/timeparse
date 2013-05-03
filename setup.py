import os
from distutils.core import setup

VERSION = "0.3"

setup(
    name = "timeparse", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/timeparse",
    download_url = "https://pypi.python.org/packages/source/t/timeparse/timeparse-{version}.tar.gz".format(version=VERSION),
    description = 'A python-module to parse strings to time-, date-, datetime- or timedelta-objects. Which formats are accepted is configurable. The module also provides classes to use with the argparse-module for parsing command-line arguments.',
    long_description = open('README.rst').read() if os.path.isfile('README.rst') else str(),
    py_modules = ["timeparse"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    license='GPL',
    keywords='parser parse datetime time strings',
)
