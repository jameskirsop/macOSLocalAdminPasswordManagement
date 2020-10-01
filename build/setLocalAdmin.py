from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import secrets
import random
import os
from pathlib import PurePath
import keyring
import subprocess
import re
import argparse
import binascii

public_key = '''ZZZ_PUBLICKEY_ZZZ'''

parser = argparse.ArgumentParser(description='Reset the password of the local admin account')
parser.add_argument('--initialPassword', nargs='?', help='The password of the localadmin account set by your MDM')
args = parser.parse_args()

kr=keyring.get_keyring()
kr.keychain = str(PurePath('/') / 'Library' / 'Keychains' / 'System.keychain')

with open('/usr/share/dict/words') as f:
    words = [word.strip() for word in f]
    new_password = '-'.join(secrets.choice(words) for i in range(4))

# Set the old password
if args.initialPassword:
    old_password = args.initialPassword
else:
    old_password = kr.get_password('addigy','localadmin')
if not old_password:
    raise Exception

# Attempt to Reset the Password
process = subprocess.Popen(
    f"/usr/sbin/sysadminctl -resetPasswordFor localadmin -newPassword {new_password} -adminUser localadmin -adminPassword {old_password}".split(), 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    # shell=True
    )
p_result, p_error = process.communicate()
pending_success, success = False, False
for line in p_error.decode('utf-8').splitlines():
    if not pending_success:
        pending_success = bool(re.search('] resetting password for',line))
    else:
        success = bool(re.search('Done',line))

if not success:
    print(p_error)
    with open('/Users/Shared/.encryptedLocalAdminPassword','w') as f:
        f.write('')
    raise Exception

#Store the Password in the System Keychain
kr.set_password('addigy','localadmin',new_password)

# Encrypt the Password
# local_key = RSA.import_key(open("public.pem").read())
local_key = RSA.import_key(public_key)
cipher_rsa = PKCS1_OAEP.new(local_key)
enc_data = cipher_rsa.encrypt(new_password.encode('utf-8'))

# Store the encrypted password as a fact
with open('/Users/Shared/.encryptedLocalAdminPassword','w') as f:
    f.write(binascii.hexlify(enc_data).decode('utf-8'))