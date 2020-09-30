#!/usr/bin/env python3
__author__ = 'jkirsop'
import subprocess
import sys

name = "Encrypted Local Admin Password"

def fact():
    cmd = "cat /Users/Shared/.encryptedLocalAdminPassword"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode('utf-8').strip()

sys.stdout.write(str(fact()))