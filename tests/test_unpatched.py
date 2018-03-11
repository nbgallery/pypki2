#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

import pypki2.config
import unittest
import sys

if sys.version_info.major == 3:
    import http.client
elif sys.version_info.major == 2:
    if sys.version_info.minor < 7 or sys.version_info.micro < 9:
        raise Exception('ssl.SSLContext is only supported by Python 2.7.9+.  You are running Python {0}.{1}.{2}.  Consider using Python 3.3+.'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    else:
        import httplib
else:
    raise Exception('Version {0}.{1} is an unknown version of Python.'.format(sys.version_info.major, sys.version_info.minor))

if sys.version_info.major == 3:
    _orig_HTTPSConnection_init = http.client.HTTPSConnection.__init__
elif sys.version_info.major == 2:
    _orig_HTTPSConnection_init = httplib.HTTPSConnection.__init__
else:
    raise Exception('Error getting original HTTPSConnection constructor.  Unexpected Python version {0}'.format(sys.version_info.major))

class NotPatchedTest(unittest.TestCase):
    def test_really_not_patched(self):
        if sys.version_info.major == 3:
            self.assertEqual(http.client.HTTPSConnection.__init__, _orig_HTTPSConnection_init)
        elif sys.version_info.major == 2:
            self.assertEqual(httplib.HTTPSConnection.__init__, _orig_HTTPSConnection_init)
        else:
            self.fail('Unknown Python version')
