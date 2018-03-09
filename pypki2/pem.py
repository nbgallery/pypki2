# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2Exception
from .utils import confirm_password, get_password

from functools import partial

try:
    import ssl
except ImportError:
    raise PyPKI2Exception('Cannot use pypki2.  This instance of Python was not compiled with SSL support.  Try installing openssl-devel and recompiling.')

import OpenSSL.crypto

def _write_pem_with_password(pkey, file_obj, password):
    _write_pem(pkey, file_obj, password=password)

def _write_temp_pem(pkey, file_obj):
    _write_pem(pkey, file_obj)

def _write_pem(pkey, file_obj, password=None):
    if password is not None:
        pem_key_data = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pkey.get_privatekey(), 'blowfish', password)
    else:
        pem_key_data = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pkey.get_privatekey())

    pem_cert_data = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, pkey.get_certificate())
    file_obj.write(pem_key_data)

    if sys.version_info.major == 3:
        file_obj.write(bytes('\n', encoding='utf-8'))
    elif sys.version_info.major == 2:
        file_obj.write('\n')

    file_obj.write(pem_cert_data)
    file_obj.flush()

class CALoader(object):
    def __init__(self, config):
        self.name = 'PEM Certificate Authority'
        self.config = config
        self.filename = None
        self.ready = False

    def is_configured(self):
        if self.config.has('ca') and len(self.config.get('ca')) > 0 and os.path.exists(self.config.get('ca')):
            return True

        return False

    def configure(self):
        if self.is_configured():
            self.filename = self.config.get('ca')
        else:
            self.filename = get_cert_path('Path to your certificate authority (CA) file: ')
            self.config.set('ca', self.filename)

        self.ready = True

def _load_pem(filename, password):
    with open(filename, 'rb') as f:
        pem = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read(), password)
    return pem

class PEMLoader(object):
    def __init__(self, config):
        self.name = 'PEM'
        self.config = config
        self.filename = None
        self.password = None
        self.ready = False

    def is_configured(self):
        # .pem info in .mypki
        if self.config.has('pem') and 'path' in self.config.get('pem'):
            return True

        return False

    def configure(self):
        if self.is_configured():
            self.filename = self._combine_pem_files(self.config.get('pem'))

            input_func = partial(get_password, self.filename)
            load_func = partial(_load_pem, self.filename)
            self.password = confirm_password(input_func, load_func)
            self.ready = True

        # no .pem info in .mypki
        else:
            self.filename = self._combine_pem_files(self._get_pem_paths())

            input_func = partial(get_password, self.filename)
            load_func = partial(_load_pem, self.filename)
            self.password = confirm_password(input_func, load_func)
            self.config.set('pem', { 'path': self.filename })
            self.ready = True

    def new_context(self, protocol=ssl.PROTOCOL_SSLv23):
        c = ssl.SSLContext(protocol)
        c.load_cert_chain(self.filename, password=self.password)
        return c

    def dump_key(self, file_obj):
        pem = _load_pem(self.filename, self.password)
