from SystemConfiguration import SCDynamicStoreCopyConsoleUser
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
import random

public_key = '''ZZZ_PUBLICKEY_ZZZ'''

parser = argparse.ArgumentParser(description='Reset the password of the local admin account')
parser.add_argument('--initialPassword', nargs='?', help='The password of the localadmin account set by your MDM')
parser.add_argument('--noGrantSecureToken', action='store_true', help='For 10.15 or earlier machines to bypass the secureToken grant section of this script')
args = parser.parse_args()

# Check to make sure a localadmin account exists, and is an admin.
cmd = "dscl . -read /Groups/admin GroupMembership"
p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
out, err = p.communicate()
if 'localadmin' not in out.decode('utf-8').split():
    raise Exception('No localadmin administrative user present on system')

kr=keyring.get_keyring()
kr.keychain = str(PurePath('/') / 'Library' / 'Keychains' / 'System.keychain')

cmd = "sysadminctl -secureTokenStatus localadmin"
p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
#sysadminctl returns Secure Token Status on StdErr...
localAdminSecureTokenDisabled = bool(re.search('Secure token is DISABLED',err.decode('utf-8')))

with open('/usr/share/dict/words') as f:
    words = [word.strip() for word in f]
    new_password = '-'.join(secrets.choice(words) for i in range(4))

# If we're enabling FV Unlock we need to remove some characters so that when we pass a command to Dialog.app it doesn't interpret some characters
if localAdminSecureTokenDisabled:
    new_password = f"{random.randint(10,1000)}{random.choice('-+=/{}:')}{new_password}{random.choice('-+=/{}:')}{random.randint(10,1000)}"
else:
    new_password = f"{random.randint(10,1000)}{random.choice('!@$%^&*()-+=/*{}?<>;:[]')}{new_password}{random.choice('!@$%^&*()-+=/*{}?<>;:[]')}{random.randint(10,1000)}"

# Get the current password
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
    raise Exception

# Encrypt the Password
local_key = RSA.import_key(public_key)
cipher_rsa = PKCS1_OAEP.new(local_key)
enc_data = cipher_rsa.encrypt(new_password.encode('utf-8'))

# Store the encrypted password as a fact
with open('/Users/Shared/.encryptedLocalAdminPassword','w') as f:
    f.write(binascii.hexlify(enc_data).decode('utf-8'))

#Store the Password in the System Keychain
kr.set_password('addigy','localadmin',new_password)


# Provide a Secure Token to localadmin
if (not args.noGrantSecureToken) and localAdminSecureTokenDisabled:
    # if args.promptUser:
    logged_in_username, logged_in_userid = (SCDynamicStoreCopyConsoleUser(None, None, None) or [None])[0:2]
    logged_in_username = [logged_in_username, ""][logged_in_username in [u"loginwindow", None, u""]]
    cmd = "sysadminctl -secureTokenStatus %s" % logged_in_username
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if re.search('Secure token is ENABLED',err.decode('utf-8')):
        cmd = f"launchctl asuser {logged_in_userid} sudo -u {logged_in_username} /Applications/Utilities/Dialog.app/Contents/MacOS/Dialog --type alert --message 'We need your password to enable a remote support account!\n\nWhen you click OK you will be prompted with a macOS password prompt.' -n /Library/Application\ Support/Dialog/dialog_banner_small.png -s --title 'Password Required' --button1shellaction '/usr/sbin/sysadminctl interactive -secureTokenOn localadmin -password {new_password}'"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out,err = p.communicate()
        print(err)
    else:
        print('Secure Token is Disabled for the current user. Unable to unlock to provide localadmin a token.')
