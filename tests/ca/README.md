Make sure you have cfssl installed in order to generate the test certs:

https://github.com/cloudflare/cfssl/blob/master/BUILDING.md

Running ```make``` will generate a self-signed root certificate authority (CA), a server cert signed by said CA, and a user cert signed by said CA.  The server's cert password is ```serverpass``` and the user's cert password is ```userpass```.  See simple_https_server.py and test_curl.sh for examples on how the certs are used.

Based on these instructions:

https://github.com/cloudflare/cfssl#generating-certificate-signing-request-and-private-key

https://github.com/cloudflare/cfssl#generating-self-signed-root-ca-certificate-and-private-key
