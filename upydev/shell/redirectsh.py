# encoding: utf-8
# from IPython to avoid loading dependency time
# https://github.com/ipython/ipython/blob/master/IPython/utils/io.py
"""
IO related utilities.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import atexit
import os
import sys

# setup stdin/stdout/stderr to sys.stdin/sys.stdout/sys.stderr
devnull = open(os.devnull, 'w')
atexit.register(devnull.close)


class Tee(object):
    """A class to duplicate an output stream to stdout/err.
    This works in a manner very similar to the Unix 'tee' command.
    When the object is closed or deleted, it closes the original file given to
    it for duplication.
    """
    # Inspired by:
    # http://mail.python.org/pipermail/python-list/2007-May/442737.html

    def __init__(self, file_or_name, mode="w", channel='stdout'):
        """Construct a new Tee object.
        Parameters
        ----------
        file_or_name : filename or open filehandle (writable)
            File that will be duplicated
        mode : optional, valid mode for open().
            If a filename was give, open with this mode.
        channel : str, one of ['stdout', 'stderr']
        """
        if channel not in ['stdout', 'stderr']:
            raise ValueError('Invalid channel spec %s' % channel)

        if hasattr(file_or_name, 'write') and hasattr(file_or_name, 'seek'):
            self.file = file_or_name
        else:
            self.file = open(file_or_name, mode)
        self.channel = channel
        self.ostream = getattr(sys, channel)
        setattr(sys, channel, self)
        self._closed = False

    def close(self):
        """Close the file and restore the channel."""
        self.flush()
        setattr(sys, self.channel, self.ostream)
        self.file.close()
        self._closed = True

    def write(self, data):
        """Write data to both channels."""
        self.file.write(data)
        self.ostream.write(data)
        self.ostream.flush()

    def flush(self):
        """Flush both channels."""
        self.file.flush()
        self.ostream.flush()

    def __del__(self):
        if not self._closed:
            self.close()
