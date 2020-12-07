# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2ConfigException
from .pem import _write_pem_with_password, _write_temp_pem
from .utils import confirm_password, get_cert_path, get_password, return_password

from functools import partial
from tempfile import NamedTemporaryFile

import os

try:
    import ssl
except ImportError:
    raise PyPKI2ConfigException('Cannot use pypki2.  This instance of Python was not compiled with SSL support.  Try installing openssl-devel and recompiling.')

import OpenSSL.crypto

def _raise_if_expired(p12):
    if p12.get_certificate().has_expired():
        raise PyPKI2ConfigException('PKI certificate has expired')

def _load_p12(filename, allow_expired, password):
    with open(filename, 'rb') as f:
        p12 = OpenSSL.crypto.load_pkcs12(f.read(), password)

    if not allow_expired:
        _raise_if_expired(p12)

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

    def configure(self, password=None, allow_expired=False):
        if self.is_configured():
            self.filename = self.config.get('p12')['path']
            load_func = partial(_load_p12, self.filename, allow_expired)

            if password is not None:
                input_func = partial(return_password, password)
                self.password = confirm_password(input_func, load_func, attempts_allowed=1)
            else:
                input_func = partial(get_password, self.filename)
                self.password = confirm_password(input_func, load_func)

            self.ready = True

        # no .p12 info in .mypki
        else:
            self.filename = get_cert_path('Path to your .p12 digital signature (DS) file: ')
            load_func = partial(_load_p12, self.filename, allow_expired)

            if password is not None:
                input_func = partial(return_password, password)
                self.password = confirm_password(input_func, load_func, attempts_allowed=1)
            else:
                input_func = partial(get_password, self.filename)
                self.password = confirm_password(input_func, load_func)

            self.config.set('p12', { 'path': self.filename })
            self.ready = True

    def new_context(self, protocol=ssl.PROTOCOL_SSLv23, allow_expired=False):
        p12 = _load_p12(self.filename, allow_expired, self.password)
        ssl_context = ssl.SSLContext(protocol)
        temp_file = NamedTemporaryFile(delete=False)
        _write_pem_with_password(p12, temp_file, self.password)
        temp_file.close()

        try:
            ssl_context.load_cert_chain(temp_file.name, password=self.password)
        finally:
            # ensure temp file is always deleted
            os.unlink(temp_file.name)

        return ssl_context

    def dump_key(self, file_obj, allow_expired=False):
        p12 = _load_p12(self.filename, allow_expired, self.password)
        _write_temp_pem(p12, file_obj)
