#!/bin/bash
openssl genrsa -des3 -out private.pem 2048
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
openssl rsa -in private.pem -out private_unencrypted.pem -outform PEM

sed -e 's/$/\\/' -i '' public.pem

PUBKEY=`cat public.pem`
sed "s~'ZZZ_PUBLICKEY_ZZZ'~'$PUBKEY'~g" build/setLocalAdmin.py > setLocalAdmin.py
mv private_unencrypted.pem webservice/private.pem
rm private.pem