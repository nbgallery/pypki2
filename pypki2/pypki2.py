# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2Exception

import sys

try:
    import ssl
except ImportError:
    raise PyPKI2Exception('Cannot use pypki2.  This instance of Python was not compiled with SSL support.  Try installing openssl-devel and recompiling.')

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
    
def make_new_httpsconnection_init(loader):
    def _new_init(self, *args, **kwargs):
        protocol = ssl.PROTOCOL_SSLv23

        if 'context' in kwargs and kwargs['context'] is not None:
            ctx = kwargs['context']
            protocol = ctx.protocol

        kwargs['key_file'] = None
        kwargs['cert_file'] = None
        kwargs['context'] = loader.new_context(protocol=protocol)
        _orig_HTTPSConnection_init(self, *args, **kwargs)

    return _new_init

def _is_patched(new_init):
    if sys.version_info.major == 3:
        if http.client.HTTPSConnection.__init__ == new_init:
            return True
        elif http.client.HTTPSConnection.__init__ == _orig_HTTPSConnection_init:
            return False
        else:
            raise Exception('Error: pypki2 is not patched or unpatched')

    elif sys.version_info.major == 2:
        if httplib.HTTPSConnection.__init__.__func__ == new_init:
            return True
        elif httplib.HTTPSConnection.__init__ == _orig_HTTPSConnection_init:
            return False
        else:
            raise Exception('Error: pypki2 is not patched or unpatched')
    else:
        raise Exception('Error determining pypki2 patch status.  Unexpected Python version {0}'.format(sys.version_info.major))

def _patch(new_init):
    if sys.version_info.major == 3:
        if not _is_patched(new_init):
            http.client.HTTPSConnection.__init__ = new_init

    elif sys.version_info.major == 2:
        if not _is_patched(new_init):
            httplib.HTTPSConnection.__init__ = new_init
    else:
        raise Exception('Error replacing HTTPSConnection constructor.  Unexpected Python version {0}'.format(sys.version_info.major))

def _unpatch(new_init):
    if sys.version_info.major == 3:
        if _is_patched(new_init):
            http.client.HTTPSConnection.__init__ = _orig_HTTPSConnection_init

    elif sys.version_info.major == 2:
        if _is_patched(new_init):
            httplib.HTTPSConnection.__init__ = _orig_HTTPSConnection_init
    else:
        raise Exception('Error replacing HTTPSConnection constructor.  Unexpected Python version {0}'.format(sys.version_info.major))
    
