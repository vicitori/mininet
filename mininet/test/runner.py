#!/usr/bin/env python

"""
Run all mininet core tests
 -v : verbose output
 -quick : skip tests that take more than ~30 seconds
"""

from unittest import defaultTestLoader, TextTestRunner
import os
import sys
import re
from mininet.util import ensureRoot
from mininet.clean import cleanup
from mininet.log import setLogLevel

# ANSI color codes
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


class ColorStream(object):
    """Wrap a stream and colorize common unittest tokens.

    This implementation is tolerant to variations in unittest output
    (e.g. 'ok', 'PASSED', 'skipped') and only emits ANSI escapes when
    the wrapped stream appears to be a TTY. That avoids polluting CI
    logs that don't support colors.
    """

    def __init__(self, stream):
        self.stream = stream
        self._ok_re = re.compile(r"\b(ok)\b", re.IGNORECASE)
        self._fail_re = re.compile(r"\b(FAIL)\b", re.IGNORECASE)
        self._skipped_re = re.compile(r"\b(skipped)\b", re.IGNORECASE)

    def _should_color(self):
        """Return True when it's appropriate to emit ANSI color codes.
        Avoid coloring when underlying stream isn't a TTY.
        """
        try:
            isatty = getattr(self.stream, "isatty", None)
            return bool(isatty and isatty())
        except Exception:
            return False

    def write(self, data):
        try:
            s = str(data)
        except Exception:
            s = data
        s = self._ok_re.sub(lambda m: _GREEN + m.group(0) + _RESET, s)
        s = self._fail_re.sub(lambda m: _RED + m.group(0) + _RESET, s)
        s = self._skipped_re.sub(lambda m: _YELLOW + m.group(0) + _RESET, s)
        return self.stream.write(s)

    def flush(self):
        try:
            return self.stream.flush()
        except Exception:
            pass


def runTests(testDir, verbosity=1):
    "discover and run all tests in testDir"
    # ensure root and cleanup before starting tests
    ensureRoot()
    cleanup()
    # discover all tests in testDir
    testSuite = defaultTestLoader.discover(testDir)
    # run tests with colored output
    stream = ColorStream(sys.stdout)
    success = (
        TextTestRunner(stream=stream, verbosity=verbosity)
        .run(testSuite)
        .wasSuccessful()
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    setLogLevel("warning")
    # get the directory containing example tests
    thisdir = os.path.dirname(os.path.realpath(__file__))
    vlevel = 2 if "-v" in sys.argv else 1
    runTests(testDir=thisdir, verbosity=vlevel)
