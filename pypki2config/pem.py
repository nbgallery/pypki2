# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2ConfigException
from .utils import confirm_password, get_cert_path, get_password, make_date_str

from functools import partial

import os
import sys

try:
    import ssl
except ImportError:
    raise PyPKI2ConfigException('Cannot use pypki2.  This instance of Python was not compiled with SSL support.  Try installing openssl-devel and recompiling.')

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
        _write_temp_pem(pem, file_obj)

    def _combine_pem_files(self, path_info):
        if 'path' in path_info and 'cert' not in path_info:
            return path_info['path']
        elif 'path' in path_info and 'cert' in path_info:
            key_name = path_info['path']
            cert_name = path_info['cert']
            base_name = os.path.splitext(path_info['path'])[0]
            new_name = base_name + make_date_str() + '.pem'

            with open(new_name, 'wb') as n, open(key_name, 'rb') as k, open(cert_name, 'rb') as c:
                key_data = k.read()
                cert_data = c.read()
                n.write(key_data)

                if sys.version_info.major == 3:
                    n.write(bytes('\n', encoding='utf-8'))
                elif sys.version_info.major == 2:
                    n.write('\n')

                n.write(cert_data)

            return new_name

    def _get_pem_paths(self):
        keyFile = get_cert_path('Path to your .pem digital signature (DS) key file: ')
        keyData = self._extract_pem_key(keyFile)
        certData = self._extract_pem_cert(keyFile)
        info = { 'path': keyFile }

        if certData is None:
            certFile = get_cert_path('Path to your .pem digital signature (DS) certificate file: ')
            info['cert'] = certFile

        return info

    def _extract_pem_cert(self, filename):
        return self._extract_pem(filename, 'Bag Attributes', '-----END CERTIFICATE-----')

    def _extract_pem_key(self, filename):
        return self._extract_pem(filename, 'Bag Attributes', '-----END ENCRYPTED PRIVATE KEY-----')

    def _extract_pem(self, filename, beginStr, endStr):
        ret = None

        with open(filename, 'r') as f:
            lines = list(f.readlines())
            begin = None
            end = None

            for i, x in enumerate(lines):
                if endStr in x:
                    end = i
                    break

            if end is not None:
                for i in range(end, -1, -1):
                    if beginStr in lines[i]:
                        begin = i
                        break

                if begin is not None:
                    ret = ''.join(lines[begin:end+1])
                else:
                    ret = None
            else:
                ret = None

        return ret
