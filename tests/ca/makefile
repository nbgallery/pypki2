all: signuser

cacsrjson:
	sed 's/HOSTNAME/'`hostname -f`'/' csr.json.orig > csr.json

ca: cacsrjson
	cfssl genkey -initca csr.json | cfssljson -bare ca

key: ca
	openssl genrsa -aes128 -passout pass:password -out user-priv-key.pem 2048
	#openssl rsa -in user-priv-key.pem -passin pass:password -pubout -out user-pub-key.pem

usercsr: key
	openssl req -new -sha256 -passin pass:password -key user-priv-key.pem -out user.csr -subj "/C=US/ST=Colorado/L=Denver/O=nbgallery/OU=WWW/CN=user"

signuser: usercsr
	cfssl sign -ca ca.pem -ca-key ca-key.pem user.csr | cfssljson -bare user-pub-key

clean:
	rm ca.csr ca-key.pem ca.pem csr.json user.csr user-priv-key.pem user-pub-key.csr user-pub-key.pem
