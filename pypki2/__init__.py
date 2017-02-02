#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

from datetime import datetime
from functools import partial
from getpass import getpass
from tempfile import NamedTemporaryFile
from time import sleep

import json
import os
import sys

if sys.version_info.major == 3:
    import http.client
elif sys.version_info.major == 2:
    if sys.version_info.minor < 7 or sys.version_info.micro < 9:
        raise Exception('ssl.SSLContext is only supported by Python 2.7.9+.  You are running Python {0}.{1}.{2}.  Consider using Python 3.3+.'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    else:
        import httplib
else:
    raise Exception('Version {0}.{1} is an unknown version of Python.'.format(sys.version_info.major, sys.version_info.minor))

class PyPKI2Exception(Exception):
    pass

try:
    import ssl
except ImportError:
    raise PyPKI2Exception('Cannot use pypki2.  This instance of Python was not compiled with SSL support.  Try installing openssl-devel and recompiling.')

try:
    import OpenSSL.crypto
    _openssl_support = True
except ImportError:
    _openssl_support = False

try:
    from IPython import get_ipython
    _ipython_support = True
    _in_ipython = False
    if get_ipython() is not None:
        _in_ipython = True
    else:
        _in_ipython = False
except ImportError:
    _ipython_support = False
    _in_ipython = False

class _Configuration(object):
    def __init__(self, filename=None):
        self.config = {}
        self.changed = False

        if filename is not None and os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    j = json.load(f)
            except ValueError as e:
                raise PyPKI2Exception('Unable to parse your .mypki file at {0}.  Is it in JSON format?'.format(filename))

            for k,v in j.items():
                self.config[k] = v

    def set(self, k, v):
        if k in self.config and self.config[k] == v:
            pass
        else:
            self.config[k] = v
            self.changed = True

    def get(self, k):
        return self.config.get(k, None)

    def has(self, k):
        return k in self.config

    def store(self, filename):
        if self.changed:
            with open(filename, 'w') as f:
                json.dump(self.config, f)

def make_date_str():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def confirm_password(input_function, load_function):
    password = None

    while True:
        password = input_function()

        try:
            load_function(password)
        except OpenSSL.crypto.Error as e:
            print('Incorrect password for private key.  Please try again.')
            continue
        else:
            print('Successfully loaded private key.')
            break

    return password

def get_password(filename):
    if sys.version_info.major == 3:
        return bytes(getpass('PKI password for {0}: '.format(filename)), encoding='utf-8')
    elif sys.version_info.major == 2:
        return getpass('PKI password for {0}: '.format(filename))
    else:
        raise PyPKI2Exception('Unknown version of Python.')

def get_cert_path(prompt):
    path = None

    while True:
        if sys.version_info.major == 3:
            path = input(prompt)
        elif sys.version_info.major == 2:
            path = raw_input(prompt)

        if os.path.exists(path):
            break
        else:
            print('Path {0} does not exist.  Please try again.'.format(path))
            continue

    return path

def _write_pem_with_password(pkey, file_obj, password):
    _write_pem(pkey, file_obj, password=password)

def _write_temp_pem(pkey, file_obj):
    _write_pem(pkey, file_obj)

def _write_pem(pkey, file_obj, password=None):
    if _openssl_support:
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

    else:
        raise PyPKI2Exception('OpenSSL package not available.  Cannot convert to .pem.')

class _CALoader(object):
    def __init__(self, config):
        self.config = config
        self.filename = None
        self.complete = False

        if self.config.has('ca') and len(self.config.get('ca')) > 0 and os.path.exists(self.config.get('ca')):
            self.filename = self.config.get('ca')
        else:
            self.filename = get_cert_path('Path to your certificate authority (CA) file: ')
            self.config.set('ca', self.filename)

        self.complete = True

def _load_p12(filename, password):
    if _openssl_support:
        with open(filename, 'rb') as f:
            p12 = OpenSSL.crypto.load_pkcs12(f.read(), password)
        return p12
    else:
        raise PyPKI2Exception('OpenSSL package not available.  Cannot load .p12 file.')

class _P12Loader(object):
    def __init__(self, config):
        self.config = config
        self.filename = None
        self.password = None
        self.complete = False

        # .p12 file info already in .mypki
        if self.config.has('p12') and 'path' in self.config.get('p12') and _openssl_support:
            self.filename = self.config.get('p12')['path']

            input_func = partial(get_password, self.filename)
            load_func = partial(_load_p12, self.filename)
            self.password = confirm_password(input_func, load_func)
            self.complete = True

        # no .p12 info in .mypki
        elif _openssl_support:
            self.filename = get_cert_path('Path to your .p12 digital signature (DS) file: ')

            input_func = partial(get_password, self.filename)
            load_func = partial(_load_p12, self.filename)
            self.password = confirm_password(input_func, load_func)
            self.config.set('p12', { 'path': self.filename })
            self.complete = True

        else:
            self.complete = False

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
        if _openssl_support:
            p12 = _load_p12(self.filename, self.password)
            _write_temp_pem(p12, file_obj)
        else:
            raise PyPKI2Exception('OpenSSL package not available.  Cannot create temporary PKI file.')

def _load_pem(filename, password):
    if _openssl_support:
        with open(filename, 'rb') as f:
            pem = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read(), password)
        return pem
    else:
        raise PyPKI2Exception('OpenSSL package not available.  Cannot load .pem file.')

class _PEMLoader(object):
    def __init__(self, config):
        self.config = config
        self.filename = None
        self.password = None
        self.complete = False

        # .pem info in .mypki
        if self.config.has('pem') and 'path' in self.config.get('pem'):
            self.filename = self._combine_pem_files(self.config.get('pem'))

            input_func = partial(get_password, self.filename)
            load_func = partial(_load_pem, self.filename)
            self.password = confirm_password(input_func, load_func)
            self.complete = True

        # no .pem info in .mypki
        else:
            self.filename = self._combine_pem_files(self._get_pem_paths())

            input_func = partial(get_password, self.filename)
            load_func = partial(_load_pem, self.filename)
            self.password = confirm_password(input_func, load_func)
            self.config.set('pem', { 'path': self.filename })
            self.complete = True

    def new_context(self, protocol=ssl.PROTOCOL_SSLv23):
        c = ssl.SSLContext(protocol)
        c.load_cert_chain(self.filename, password=self.password)
        return c

    def dump_key(self, file_obj):
        if _openssl_support:
            pem = _load_pem(self.filename, self.password)
            _write_temp_pem(pem, file_obj)
        else:
            raise PyPKI2Exception('OpenSSL package not available.  Cannot create temporary PKI file.')

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

def mypki_config_path():
    if 'MYPKI_CONFIG' in os.environ:
        p = os.environ['MYPKI_CONFIG'].strip()
        d = os.path.split(p)[0]

        if os.path.exists(d) and os.path.isdir(d):
            return p+os.sep+'mypki_config'
        elif os.path.exists(d):
            return p
        else:
            return None

    return None

def home_config_path():
    if 'HOME' in os.environ:
        p = os.environ['HOME']

        if os.path.exists(p):
            return p+os.sep+'.mypki'
        else:
            return None

    return None

def get_config_path():
    p = mypki_config_path()

    if p is not None:
        return p

    p = home_config_path()

    if p is not None:
        return p

    raise PyPKI2Exception('Could not find MYPKI_CONFIG or HOME environment variables.  If you are on Windows, you need to add a MYPKI_CONFIG environment variable in Control Panel.  See Windows Configuration in README.md for further instructions.')

class _Loader(object):
    def __init__(self):
        self.config_path = get_config_path()
        self.ipython_config()
        self.config = None
        self.loader = None
        self.ca_loader = None

    def ipython_config(self):
        temp_config = _Configuration(self.config_path)
        if temp_config.has('p12') and 'path' in temp_config.get('p12'):
            pass
        else:
            if _in_ipython:
                from IPython.display import display, Javascript
                display(Javascript("MyPKI.init({'no_verify':true, configure:true});"))
                print('Configuring .mypki via JavaScript .p12 dialog...')
                while True:
                    temp_config = _Configuration(self.config_path)
                    if temp_config.has('p12') and 'path' in temp_config.get('p12'):
                        break
                    else:
                        sleep(2)

    def prepare_loader(self):
        if self.loader is None:
            self.config = _Configuration(self.config_path)
            loaders = [ _P12Loader, _PEMLoader ]

            for loader in loaders:
                evaluated_loader = loader(self.config)

                if evaluated_loader.complete:
                    self.loader = evaluated_loader
                    break

            if self.loader is None:
                raise PyPKI2Exception('None of the PKI loaders succeeded.')

            self.ca_loader = _CALoader(self.config)
            self.config.store(self.config_path)

    def new_context(self, protocol=ssl.PROTOCOL_SSLv23):
        self.prepare_loader()
        c = self.loader.new_context(protocol=protocol)
        c.verify_mode = ssl.CERT_REQUIRED
        ca_filename = self.ca_loader.filename.strip()

        if len(ca_filename) == 0:
            raise PyPKI2Exception('Certificate Authority (CA) file not specified.')
        elif not os.path.exists(ca_filename):
            raise PyPKI2Exception('Certificate Authority (CA) file {0} does not exist.'.format(ca_filename))
        else:
            c.load_verify_locations(cafile=ca_filename)

        return c

    def dump_key(self, fobj):
        self.prepare_loader()
        self.loader.dump_key(fobj)

    def ca_path(self):
        self.prepare_loader()
        return self.ca_loader.filename

_pypki_loader = _Loader()

if sys.version_info.major == 3:
    _orig_HTTPSConnection_init = http.client.HTTPSConnection.__init__
elif sys.version_info.major == 2:
    _orig_HTTPSConnection_init = httplib.HTTPSConnection.__init__
else:
    raise Exception('Error getting original HTTPSConnection constructor.  Unexpected Python version {0}'.format(sys.version_info.major))
    
def _new_init(self, *args, **kwargs):
    protocol = ssl.PROTOCOL_SSLv23

    if 'context' in kwargs and kwargs['context'] is not None:
        ctx = kwargs['context']
        protocol = ctx.protocol

    kwargs['key_file'] = None
    kwargs['cert_file'] = None
    kwargs['context'] = _pypki_loader.new_context(protocol=protocol)
    _orig_HTTPSConnection_init(self, *args, **kwargs)

if sys.version_info.major == 3:
    http.client.HTTPSConnection.__init__ = _new_init
elif sys.version_info.major == 2:
    httplib.HTTPSConnection.__init__ = _new_init
else:
    raise Exception('Error replacing HTTPSConnection constructor.  Unexpected Python version {0}'.format(sys.version_info.major))

def dump_key(fobj):
    _pypki_loader.dump_key(fobj)

def ca_path():
    return _pypki_loader.ca_path()
