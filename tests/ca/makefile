all: fetch root_ca_cert intermediate_cert

clean:
	rm -rf certs crl index.txt intermediate newcerts openssl.cnf private serial

fetch_root:
	wget https://jamielinux.com/docs/openssl-certificate-authority/_downloads/root-config.txt
	sed -i -e 's/\/root\/ca/./' root-config.txt
	sed -i -e 's/emailAddress_default            =/emailAddress_default            = testing@testing.com/' root-config.txt
	mv root-config.txt openssl.cnf

fetch_intermediate: intermediate_dirs
	wget https://jamielinux.com/docs/openssl-certificate-authority/_downloads/intermediate-config.txt
	sed -i -e 's/\/root\/ca\/intermediate/./' intermediate-config.txt
	sed -i -e 's/emailAddress_default            =/commonName_default = foo\nemailAddress_default            = testing@testing.com/' intermediate-config.txt
	sed -i -e 's/organizationalUnitName_default  =/organizationalUnitName_default  = Test Certificate Authority/' intermediate-config.txt
	mv intermediate-config.txt intermediate/openssl.cnf

fetch: fetch_root fetch_intermediate

root_dirs:
	mkdir -p certs crl newcerts private
	chmod 700 private
	touch index.txt
	echo 1000 > serial

root_ca_key: root_dirs
	openssl genrsa -aes256 -out private/ca.key.pem 4096
	chmod 400 private/ca.key.pem

root_ca_cert: root_dirs root_ca_key
	openssl req -config openssl.cnf -key private/ca.key.pem -new -x509 -days 100000 -sha256 -extensions v3_ca -out certs/ca.cert.pem
	chmod 444 certs/ca.cert.pem

intermediate_dirs:
	mkdir -p intermediate
	mkdir -p intermediate/certs
	mkdir -p intermediate/crl
	mkdir -p intermediate/csr
	mkdir -p intermediate/newcerts
	mkdir -p intermediate/private
	chmod 700 intermediate/private
	touch intermediate/index.txt
	echo 1000 > intermediate/serial
	echo 1000 > intermediate/crlnumber

intermediate_key: intermediate_dirs
	openssl genrsa -aes256 -out intermediate/private/intermediate.key.pem 4096
	chmod 400 intermediate/private/intermediate.key.pem

intermediate_signature_request: intermediate_key
	openssl req -config intermediate/openssl.cnf -new -sha256 -key intermediate/private/intermediate.key.pem -out intermediate/csr/intermediate.csr.pem

intermediate_cert: intermediate_signature_request
	openssl ca -config openssl.cnf -extensions v3_intermediate_ca -days 100000 -notext -md sha256 -in intermediate/csr/intermediate.csr.pem -out intermediate/certs/intermediate.cert.pem
