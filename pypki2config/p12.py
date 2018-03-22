# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2ConfigException
from .pem import _write_pem_with_password, _write_temp_pem
from .utils import confirm_password, get_cert_path, get_password

from functools import partial
from tempfile import NamedTemporaryFile

import os

try:
    import ssl
except ImportError:
    raise PyPKI2ConfigException('Cannot use pypki2.  This instance of Python was not compiled with SSL support.  Try installing openssl-devel and recompiling.')

import OpenSSL.crypto

def _load_p12(filename, password):
    with open(filename, 'rb') as f:
        p12 = OpenSSL.crypto.load_pkcs12(f.read(), password)
    return p12

class P12Loader(object):
    def __init__(self, config):
        self.name = 'PKCS12'
        self.config = config
        self.filename = None
        self.password = None
        self.ready = False

    def is_configured(self):
        # .p12 file info already in .mypki
        if self.config.has('p12') and 'path' in self.config.get('p12'):
            return True

        return False

    def configure(self):
        if self.is_configured():
            self.filename = self.config.get('p12')['path']

            input_func = partial(get_password, self.filename)
            load_func = partial(_load_p12, self.filename)
            self.password = confirm_password(input_func, load_func)
            self.ready = True

        # no .p12 info in .mypki
        else:
            self.filename = get_cert_path('Path to your .p12 digital signature (DS) file: ')

            input_func = partial(get_password, self.filename)
            load_func = partial(_load_p12, self.filename)
            self.password = confirm_password(input_func, load_func)
            self.config.set('p12', { 'path': self.filename })
            self.ready = True

    def new_context(self, protocol=ssl.PROTOCOL_SSLv23):
        p12 = _load_p12(self.filename, self.password)
        c = ssl.SSLContext(protocol)
        f = NamedTemporaryFile(delete=False)
        _write_pem_with_password(p12, f, self.password)
        f.close()
        c.load_cert_chain(f.name, password=self.password)
        os.unlink(f.name)
        return c

    def dump_key(self, file_obj):
        p12 = _load_p12(self.filename, self.password)
        _write_temp_pem(p12, file_obj)
