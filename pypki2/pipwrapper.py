#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

from tempfile import NamedTemporaryFile

import pypki2.config

try:
    import pip
except ImportError:
    raise pypki2.PyPKI2Exception('Unable to import pip.  Cannot start pipwrapper.')

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
        pypki2.config.dump_key(temp_key)
        new_args.append('--client-cert={0}'.format(temp_key.name))
        new_args.append('--cert={0}'.format(pypki2.config.ca_path()))
        new_args.append('--disable-pip-version-check')
        _orig_pip_main(new_args)

pip.main = _new_pip_main
