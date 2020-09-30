#!/bin/bash
# cp build/setLocalAdmin.py .
pubkey=`cat public.pem`
sed "s~ZZZ_PUBLICKEY_ZZZ~$pubkey~g" build/setLocalAdmin.py > setLocalAdmin.py
mv private_unencrypted.pem webservice/private.pem
rm private.pem