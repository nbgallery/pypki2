# vim: expandtab tabstop=4 shiftwidth=4

from .pypki2 import _is_patched, make_new_httpsconnection_init, _patch, _unpatch
from .config import Loader

_new_httpsconnection_init = make_new_httpsconnection_init(Loader())

def patch():
    _patch(_new_httpsconnection_init)

def unpatch():
    _unpatch(_new_httpsconnection_init)

def is_patched():
    return _is_patched(_new_httpsconnection_init)

patch()
