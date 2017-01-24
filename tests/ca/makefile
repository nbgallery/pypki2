all: key

csrjson:
	sed 's/HOSTNAME/'`hostname -f`'/' csr.json.orig > csr.json

ca: csrjson
	cfssl genkey -initca csr.json | cfssljson -bare ca

key: ca
	openssl genrsa -aes128 -passout pass:password -out user-priv-key.pem 2048
	openssl rsa -in user-priv-key.pem -passin pass:password -pubout -out user-pub-key.pem
