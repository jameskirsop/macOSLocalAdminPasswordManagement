#!/usr/bin/env python3
__author__ = 'jkirsop'
import sys
import os
import datetime

name = "Encrypted Local Admin Password - Days since last change"

def fact():
    try:
        timestamp = os.path.getmtime('/Users/Shared/.encryptedLocalAdminPassword')
    except FileNotFoundError:
        timestamp = datetime.datetime.now().timestamp()
    datetime.datetime.fromtimestamp(timestamp)
    difference = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
    return difference.days

sys.stdout.write(str(fact()))