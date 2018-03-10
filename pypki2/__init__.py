# vim: expandtab tabstop=4 shiftwidth=4

from .pypki2 import _is_patched, make_new_init, _patch, _unpatch
from .config import Loader

_pypki_loader = Loader()
_new_init = make_new_init(_pypki_loader)

def patch():
    _patch(_new_init)

def unpatch():
    _unpatch(_new_init)

def is_patched():
    return _is_patched(_new_init)

def dump_key(fobj):
    _pypki_loader.dump_key(fobj)

def ca_path():
    return _pypki_loader.ca_path()
