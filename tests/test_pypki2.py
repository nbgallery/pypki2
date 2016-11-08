#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

import unittest
import pypki2
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
    def test_basic_fetch(self):
        resp = urlopen('https://github.com/nbgallery/pypki2.git')
        d = bin_to_utf8(resp.read())
        print(d)
