#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2PipException

from pypki2config import ca_path, dump_key
from tempfile import NamedTemporaryFile

try:
    import pip as _pip
except ImportError:
    raise PyPKI2PipException('Unable to import pip.  Cannot start pipwrapper.')

def pip_pki_exec(executor):
    args = []
    executor_returned = None

    with NamedTemporaryFile() as temp_key:
        dump_key(temp_key)
        args.append('--client-cert={0}'.format(temp_key.name))
        args.append('--cert={0}'.format(ca_path()))
        args.append('--disable-pip-version-check')
        executor_returned = executor(args)

    return executor_returned

def pip(*args, **kwargs):
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
        _pip.main(new_args)
