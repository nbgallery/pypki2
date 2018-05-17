# vim: expandtab tabstop=4 shiftwidth=4

from .pypki2 import _is_patched, make_new_httpsconnection_init, _patch, _unpatch

from pypki2config import configured_loader

_new_httpsconnection_init = make_new_httpsconnection_init(configured_loader)
_pypki_loader = configured_loader  # added for backwards compatibility (issue 22)

def patch():
    _patch(_new_httpsconnection_init)

def unpatch():
    _unpatch(_new_httpsconnection_init)

def is_patched():
    return _is_patched(_new_httpsconnection_init)

patch()
