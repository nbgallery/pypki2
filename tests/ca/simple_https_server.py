#!/usr/bin/env python

# vim: expandtab tabstop=4 shiftwidth=4

from http.server import HTTPServer, SimpleHTTPRequestHandler
from ssl import wrap_socket

httpd = HTTPServer(('0.0.0.0', 4443), SimpleHTTPRequestHandler)
httpd.socket = wrap_socket(httpd.socket, keyfile='server-priv-key.pem', certfile='server-pub-key.pem', server_side=True)
httpd.serve_forever()
