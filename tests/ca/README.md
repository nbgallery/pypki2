Make sure you have cfssl installed in order to generate the test certs:

https://github.com/cloudflare/cfssl/blob/master/BUILDING.md

Running ```make``` will generate a self-signed root certificate authority (CA), based on these instructions:

https://github.com/cloudflare/cfssl#generating-certificate-signing-request-and-private-key
https://github.com/cloudflare/cfssl#generating-self-signed-root-ca-certificate-and-private-key
