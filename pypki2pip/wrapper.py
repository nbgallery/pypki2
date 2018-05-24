#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2PipException

from os import unlink
from pypki2config import ca_path, dump_key
from tempfile import NamedTemporaryFile

def pip_pki_exec(executor):
    args = []
    executor_returned = None

    temp_key = NamedTemporaryFile(delete=False)
    dump_key(temp_key)
    temp_key.close()

    args.append('--client-cert={0}'.format(temp_key.name))
    args.append('--cert={0}'.format(ca_path()))
    args.append('--disable-pip-version-check')

    try:
        executor_returned = executor(args)
    finally:
        #ensure temp file is always deleted
        unlink(temp_key.name)

    return executor_returned

def pip(*args, **kwargs):
    try:
        import pip as _pip
    except ImportError:
        raise PyPKI2PipException('Unable to import pip.  Cannot start pipwrapper.')

    new_args = []

    if 'args' in kwargs:
        new_args = kwargs['args']
    elif len(args) > 0 and len(args[0]) > 0:
        new_args = args[0]

    new_args = [ arg for arg in new_args if '--client-cert=' not in arg ]
    new_args = [ arg for arg in new_args if '--cert=' not in arg ]

    #create the temp key and dump cert and key to it
    temp_key = NamedTemporaryFile(delete=False)
    dump_key(temp_key)
    temp_key.close()    
    
    #use file in args
    new_args.append('--client-cert={0}'.format(temp_key.name))
    new_args.append('--cert={0}'.format(ca_path()))
    new_args.append('--disable-pip-version-check')
        
    try:
        _pip.main(new_args)
    finally:
        #ensure temp file is always deleted
        unlink(temp_key.name)
