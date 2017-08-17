#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

from functools import partial

import pypki2
import unittest
import sys

if sys.version_info.major == 3:
    from urllib.request import urlopen
elif sys.version_info.major == 2:
    from urrlib2 import urlopen

def bin_to_utf8(s):
    if sys.version_info.major == 3:
        return str(s, encoding='utf8')
    elif sys.version_info.major == 2:
        return unicode(s)

class GitHubTest(unittest.TestCase):
    def notest_basic_fetch(self):
        resp = urlopen('https://github.com/nbgallery/pypki2.git')
        d = bin_to_utf8(resp.read())
        print(d)

class UserCertTest(unittest.TestCase):
    def test_good_pem_password(self):
        cert_path = 'tests/ca/user-priv-key.pem'
        load_func = partial(pypki2._load_pem, cert_path)
        if sys.version_info.major == 3:
            input_func = lambda: b'userpass'
            self.assertEqual(pypki2.confirm_password(input_func, load_func), b'userpass')
        elif sys.version_info.major == 2:
            input_func = lambda: 'userpass'
            self.assertEqual(pypki2.confirm_password(input_func, load_func), 'userpass')

    def test_no_pem_password(self):
        cert_path = 'tests/ca/user-priv-key-nopass.pem'
        input_func = lambda: 'userpass'  # this password shouldn't even get used
        load_func = partial(pypki2._load_pem, cert_path)

        if sys.version_info.major == 3:
            self.assertEqual(pypki2.confirm_password(input_func, load_func), b'')
        elif sys.version_info.major == 2:
            self.assertEqual(pypki2.confirm_password(input_func, load_func), '')
