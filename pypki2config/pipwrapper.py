#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

from .config import ca_path, dump_key
from .exceptions import PyPKI2ConfigException

from tempfile import NamedTemporaryFile

try:
    import pip
except ImportError:
    raise PyPKI2ConfigException('Unable to import pip.  Cannot start pipwrapper.')

_orig_pip_main = pip.main

def _new_pip_main(*args, **kwargs):
    new_args = []

    if 'args' in kwargs:
        new_args = kwargs['args']
    elif len(args) > 0 and len(args[0]) > 0:
        new_args = args[0]

    new_args = [ arg for arg in new_args if '--client-cert=' not in arg ]
    new_args = [ arg for arg in new_args if '--cert=' not in arg ]

    with NamedTemporaryFile() as temp_key:
        dump_key(temp_key)
        new_args.append('--client-cert={0}'.format(temp_key.name))
        new_args.append('--cert={0}'.format(ca_path()))
        new_args.append('--disable-pip-version-check')
        _orig_pip_main(new_args)

pip.main = _new_pip_main
