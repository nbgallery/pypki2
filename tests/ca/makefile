HOSTNAME := $(shell hostname -f)

all: signuser signserver

cacsrjson:
	sed 's/HOSTNAME/'`hostname -f`'/' csr.json.orig > csr.json

ca: cacsrjson
	cfssl genkey -initca csr.json | cfssljson -bare ca

userkey: ca
	openssl genrsa -aes128 -passout pass:userpass -out user-priv-key.pem 2048

serverkey: ca
	openssl genrsa -aes128 -passout pass:serverpass -out server-priv-key.pem 2048

usercsr: userkey
	openssl req -new -sha256 -passin pass:userpass -key user-priv-key.pem -out user.csr -subj "/C=US/ST=Colorado/L=Denver/O=nbgallery/OU=WWW/CN=user"

servercsr: serverkey
	openssl req -new -sha256 -passin pass:serverpass -key server-priv-key.pem -out server.csr -subj "/C=US/ST=Colorado/L=Denver/O=nbgallery/OU=WWW/CN=$(HOSTNAME)"

signuser: usercsr
	cfssl sign -ca ca.pem -ca-key ca-key.pem user.csr | cfssljson -bare user-pub-key

signserver: servercsr
	cfssl sign -ca ca.pem -ca-key ca-key.pem server.csr | cfssljson -bare server-pub-key

clean:
	rm ca.csr ca-key.pem ca.pem csr.json user.csr user-priv-key.pem user-pub-key.csr user-pub-key.pem server-priv-key.pem server-pub-key.csr server-pub-key.pem
