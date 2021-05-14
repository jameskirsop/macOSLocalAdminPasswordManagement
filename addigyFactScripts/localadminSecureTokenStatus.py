#!/usr/bin/env python
#!/usr/bin/python
__author__ = 'jkirsop'
import sys
import subprocess
import re

name = "LocalAdmin Account - SecureToken Enabled"

def fact():
    cmd = "sysadminctl -secureTokenStatus localadmin"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if re.search('Secure token is ENABLED',err):
        return True
    return False

sys.stdout.write(str(fact()))