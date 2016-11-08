# pypki2

pypki2 attempts to make it a bit easier to access PKI-enabled services with Python.  Conceptually, this is very similar to the Ruby MyPKI package, and is intended to use the same ~/.mypki configuration file.

Basically pypki2 "monkey-patches" the built-in HTTPSConnection class with a new loader that uses the PKI configuration in ~/.mypki.  If the .mypki file is missing, or the paths to the PKI files are missing from .mypki, then the user is prompted and the values are stored for future use; ideally the user should only have to deal with this once.  Likewise, the user is prompted for their PKI password, which only resides in memory and is never placed in permanent storage (nor should it be).

## Examples

### Simply fetching a URL
The most basic form of request can just use urlopen.  Python automatically uses the HTTPSConnection for URL's that start with https:, so you don't have to do anything special after you import pypki2.

#### Python 3.4+
```python
import pypki2

from urllib.request import urlopen

resp = urlopen('https://your.pki.enabled.website/path/to/whatever')
print(str(resp.read(), encoding='utf-8'))
```

#### Python 2.7.9+
```python
import pypki2

from urllib2 import urlopen

resp = urlopen('https://your.pki.enabled.website/path/to/whatever')
print(resp.read())
```

### Sending requests to more complex PKI-enabled services

Some more complex services use cookies to track PKI sessions, so you have to add support for cookies in your URL opener.  Thankfully, this is fairly straight forward.  Notice that the HTTPSHandler does not require any parameters because it uses HTTPSConnection, which has been overwridden by pypki2.

#### Python 3.4+
```python
import pypki2

from urllib.request import build_opener, HTTPCookieProcessor, HTTPSHandler, Request

opener = build_opener(HTTPCookieProcessor(), HTTPSHandler())
req = Request('https://your.other.pki.enabled.website/path/to/whatever')
resp = opener.open(req)
print(str(resp.read(), encoding='utf-8'))
```

#### Python 2.7.9+
```python
import pypki2

from urllib2 import build_opener, HTTPCookieProcessor, HTTPSHandler, Request

opener = build_opener(HTTPCookieProcessor(), HTTPSHandler())
req = Request('https://your.other.pki.enabled.website/path/to/whatever')
resp = opener.open(req)
print(resp.read())
```

### High Performance Connections

In some cases where you'll be communicating with a server at high speed, it can be helpful to hold onto your HTTPSConnection object rather than reconnecting each time.  Since pypki2 simply overrides the SSLContext creation and leaves everything else alone, you can still use HTTPSConnections directly as documented in Python standard library reference.  It's also worth mentioning that by default, Python sets the protocol to HTTP 1.1, which is suitable for connection reuse.  Examples follow...

#### Python 3.4+
```python
from http.client import HTTPSConnection
import pypki2

my_connection = HTTPSConnection('your.pki.enabled.service')
my_queries = [ ... ]
my_results = []

for query in my_queries:
    my_connection.request('GET', '/rest/endpoint/'+query, headers={'accept': 'application/json'})

    try:
        resp = my_connection.getresponse()
    except Exception as e:
        print(e)
        break

    my_results.append(resp.read())

my_connection.close()
```

#### Python 2.7.9+
```python
from httplib import HTTPSConnection
import pypki2

my_connection = HTTPSConnection('your.pki.enabled.service')
my_queries = [ ... ]
my_results = []

for query in my_queries:
    my_connection.request('GET', '/rest/endpoint/'+query, headers={'accept': 'application/json'})

    try:
        resp = my_connection.getresponse()
    except Exception as e:
        print(e)
        break

    my_results.append(resp.read())

my_connection.close()
```

### Overriding the protocol

Some recalcitrant servers require a very specific SSL protocol version.  For these difficult times, pypki2 allows you to pass a specific protocol via the context keyword passed to ssl.SSLContext.  Note that pypki2 will create a new SSLContext instance containing your PKI info, but it will use the protocol you specified in the SSLContext instance you created to pass to HTTPSHandler.  This makes more sense in the examples below...

#### Python 3.4+
```python
import pypki2
import ssl

from urllib.request import build_opener, HTTPCookieProcessor, HTTPSHandler, Request

opener = build_opener(HTTPCookieProcessor(), HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv3))
req = Request('https://your.difficult.pki.enabled.server/path/you/really/need')
resp = opener.open(req)
print(str(resp.read(), encoding='utf-8'))
```

#### Python 2.7.9+
```python
import pypki2
import ssl

from urllib2 import build_opener, HTTPCookieProcessor, HTTPSHandler, Request

opener = build_opener(HTTPCookieProcessor(), HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv3))
req = Request('https://your.difficult.pki.enabled.server/path/you/really/need')
resp = opener.open(req)
print(resp.read())
```

### ```pip``` Wrapper

This package also provides a wrapper for pip's ```main()``` function, which can be useful when you need to install packages from within your code.  Note that this feature only works if you have the OpenSSL package available.  Here's an example:

```python
import pip
import pypki2.pipwrapper

index_url = 'https://your.pki.enabled.pip.server/simple/'
extra_index_url = 'http://pypi.python.org/pypi/'
trusted_host = 'pypi.python.org'
package_name = 'awesomepackage'

pip.main([
    'install',
    '-vvv',
    '--index-url={0}'.format(index_url),
    '--extra-index-url={0}'.format(extra_index_url),
    '--trusted-host={0}'.format(trusted_host),
    '--user',
    '--allow-external={0}'.format(package_name),
    '--timeout=30',
    '--retries=20',
    '--allow-unverified={0}'.format(package_name),
    package_name
])
```

Pypki2 will automatically fill in the ```--client-cert=``` and ```--cert=``` parameters with info from your .mypki file.  You'll only have to enter your PKI password once; normally pip requires you do enter your password multiple times as it steps through the installation transactions with the server.

## Windows Configuration
Since Windows does not define a standard HOME environment variable, you must set the MYPKI_CONFIG environment variable in Control Panel yourself.  It needs to define a location where pypki2 can store a configuration file.  For example, many corporate environments have a network drive for each user, such as H:\ or M:\johndoe\private.  Just set MYPKI_CONFIG to the path for your particular environment.  You can find the environment variable dialog box by searching for 'environment' in the Control Panel window.

Note: On Linux/MacOS, you can set MYPKI_CONFIG if you want pypki2 to store your .mypki configuration file somewhere other than your HOME directory.

## Compatibility
pypki2 has been tested with Python 2.7.10 and 3.4+.  It requires that SSL support has been compiled in; if not an exception will be thrown on import.  If the OpenSSL package is available (it's not part of the Python standard library), then pypki2 will support PKCS12 (.p12) certificates.  If the OpenSSL package is not available, then pypki2 will fall back to PEM support only via the ssl package in the standard library (again, if it was compiled in).
