# vim: expandtab tabstop=4 shiftwidth=4

from .pypki2 import patch, unpatch
from .configuration import Loader

_pypki_loader = Loader()
patch()

def dump_key(fobj):
    _pypki_loader.dump_key(fobj)

def ca_path():
    return _pypki_loader.ca_path()
