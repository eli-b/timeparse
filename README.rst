timeparse
==========

An argparse-extension for parsing command-line arguments as time-, date-,
datetime-, or timedelta-objects.

Latest Version
--------------
The latest version of this project can be found at : http://github.com/thomst/timeparse.


Installation
------------
* Option 1 : Install via pip ::

    pip install timeparse

* Option 2 : If you have downloaded the source ::

    python setup.py install


Documentation:
-------------
Please visit the documentation on readthedocs.org:
https://timeparse.readthedocs.org/en/latest/index.html


Usage
-------------
How to use? ::

    >>> import argparse
    >>> from timeparse import ParseDatetime
    >>>
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--datetime', action=ParseDatetime, nargs='+')
    >>>
    >>> parser.parse_args("--datetime 2.4.2013 23:02".split()).datetime
    datetime.datetime(2013, 4, 2, 23, 2)




Reporting Bugs
--------------
Please report bugs at github issue tracker:
https://github.com/thomst/timeparse/issues


Author
------
thomst <thomaslfuss@gmx.de>
Thomas Leichtfuß

* http://github.com/thomst
