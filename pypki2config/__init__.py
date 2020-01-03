# vim: expandtab tabstop=4 shiftwidth=4

from .config import Loader
from .exceptions import PyPKI2ConfigException

try:
    import ssl
except ImportError:
    raise PyPKI2ConfigException('Cannot use pypki2.  This instance of Python was not compiled with SSL support.  Try installing openssl-devel and recompiling.')

configured_loader = Loader()

def dump_key(fobj):
    configured_loader.dump_key(fobj)

def ca_path():
    return configured_loader.ca_path()

def ssl_context(protocol=ssl.PROTOCOL_SSLv23, password=None):
    return configured_loader.new_context(protocol=protocol, password=password)
