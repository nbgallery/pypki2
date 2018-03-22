# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2ConfigException
from .p12 import P12Loader
from .pem import CALoader, PEMLoader
from .utils import in_ipython, in_nbgallery, input23

from time import sleep

try:
    import ssl
except ImportError:
    raise PyPKI2ConfigException('Cannot use pypki2.  This instance of Python was not compiled with SSL support.  Try installing openssl-devel and recompiling.')

import json
import os

class Configuration(object):
    def __init__(self, filename=None):
        self.config = {}
        self.changed = False

        if filename is not None and os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    j = json.load(f)
            except ValueError as e:
                raise PyPKI2ConfigException('Unable to parse your .mypki file at {0}.  Is it in JSON format?'.format(filename))

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

    raise PyPKI2ConfigException('Could not find MYPKI_CONFIG or HOME environment variables.  If you are on Windows, you need to add a MYPKI_CONFIG environment variable in Control Panel.  See Windows Configuration in README.md for further instructions.')

def pick_loader(loaders):
    options = { str(i+1):loaders[i] for i in range(len(loaders)) }
    selected = None

    while selected is None:
        print('Available PKI configuration loaders are:')

        for k in sorted(list(options.keys())):
            print('{0}) {1}'.format(k, options[k].name))

        num = input23('Which type of PKI do you want to configure: ').strip()

        if num in options:
            selected = options[num]
        else:
            print('Invalid selection...')
            selection = None

    return selected

class Loader(object):
    def __init__(self):
        self.config_path = get_config_path()
        self.ipython_config()
        self.config = None
        self.loader = None
        self.ca_loader = None

    def ipython_config(self):
        temp_config = Configuration(self.config_path)
        if temp_config.has('p12') and 'path' in temp_config.get('p12'):
            pass
        else:
            if in_ipython() and in_nbgallery():
                from IPython.display import display, Javascript
                display(Javascript("MyPKI.init({'no_verify':true, configure:true});"))
                print('Configuring .mypki via JavaScript .p12 dialog...')
                while True:
                    temp_config = Configuration(self.config_path)
                    if temp_config.has('p12') and 'path' in temp_config.get('p12'):
                        break
                    else:
                        sleep(2)

    def prepare_loader(self):
        if self.loader is None:
            self.config = Configuration(self.config_path)
            loaders = [ P12Loader(self.config), PEMLoader(self.config) ]
            configured_loaders = [ loader for loader in loaders if loader.is_configured() ]

            if len(configured_loaders) == 0:
                self.loader = pick_loader(loaders)
            elif len(configured_loaders) > 0:
                self.loader = configured_loaders[0]
            else:
                raise PyPKI2ConfigException('No configured PKI loader available.')

            self.loader.configure()

            self.ca_loader = CALoader(self.config)
            self.ca_loader.configure()

            self.config.store(self.config_path)

    def new_context(self, protocol=ssl.PROTOCOL_SSLv23):
        self.prepare_loader()
        c = self.loader.new_context(protocol=protocol)
        c.verify_mode = ssl.CERT_REQUIRED
        ca_filename = self.ca_loader.filename.strip()

        if len(ca_filename) == 0:
            raise PyPKI2ConfigException('Certificate Authority (CA) file not specified.')
        elif not os.path.exists(ca_filename):
            raise PyPKI2ConfigException('Certificate Authority (CA) file {0} does not exist.'.format(ca_filename))
        else:
            c.load_verify_locations(cafile=ca_filename)

        return c

    def dump_key(self, fobj):
        self.prepare_loader()
        self.loader.dump_key(fobj)

    def ca_path(self):
        self.prepare_loader()
        return self.ca_loader.filename
