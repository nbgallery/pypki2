# vim: expandtab tabstop=4 shiftwidth=4

from .exceptions import PyPKI2ConfigException

from datetime import datetime
from getpass import getpass

import OpenSSL.crypto
import os
import sys

def input23(prompt):
    if sys.version_info.major == 3:
        return input(prompt)
    elif sys.version_info.major == 2:
        return raw_input(prompt)

def in_nbgallery():
    if 'NBGALLERY_CLIENT_VERSION' in os.environ:
        return True

    return False

def in_ipython():
    try:
        from IPython import get_ipython

        if get_ipython() is not None:
            return True
        else:
            return False

    except ImportError:
        return False

    return False

def make_date_str():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def password_is_good(load_function, password):
    try:
        load_function(password)
    except OpenSSL.crypto.Error as e:
        return False

    return True

def blank_password():
    if sys.version_info.major == 3:
        return bytes('', encoding='utf-8')
    elif sys.version_info.major == 2:
        return ''
    else:
        raise PyPKI2ConfigException('Unknown version of Python.')

def confirm_password(input_function, load_function):
    # see if we even need a password before prompting
    password = blank_password()

    if password_is_good(load_function, password):
        return password

    while True:
        password = input_function()

        if password_is_good(load_function, password):
            print('Successfully loaded private key.')
            break
        else:
            print('Incorrect password for private key.  Please try again.')
            continue

    return password

def get_password(filename):
    if sys.version_info.major == 3:
        return bytes(getpass('PKI password for {0}: '.format(filename)), encoding='utf-8')
    elif sys.version_info.major == 2:
        return getpass('PKI password for {0}: '.format(filename))
    else:
        raise PyPKI2ConfigException('Unknown version of Python.')

def get_cert_path(prompt):
    path = None

    while True:
        path = input23(prompt).strip()

        if os.path.exists(path):
            break
        else:
            print('Path {0} does not exist.  Please try again.'.format(path))
            continue

    return path
