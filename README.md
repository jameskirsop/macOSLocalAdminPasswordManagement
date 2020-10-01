# macOSLocalAdminPasswordManagement

This project has been written to allow for the rotation of a 'localadmin' account password on macOS 10.15 and newer (as Python3 is required*). It uses RSA public/private key encryption to allow secure escrow of the encrypted password to an MDM platform and has a simple micro web service that can be deployed via WSGI to allow password decryption.

_*Python3 can be installed on machine prior to 10.15. For backwards compatibility We deploy python3 to all machines 10.14 or older via installing the .pkg available from the [Python download page](https://www.python.org/downloads/mac-osx/) via a Custom Software package in Addigy. This does cause some complications and so we'll probably deprecate this support in the near future._ 

## Instructions for Deployment to the Target Machine

1. Generate your RSA Keys:
```
openssl genrsa -des3 -out private.pem 2048
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
openssl rsa -in private.pem -out private_unencrypted.pem -outform PEM
```
2. Build the deployment script. Because macOS uses a [_special_ version of `sed`](https://stackoverflow.com/questions/24275070/sed-not-giving-me-correct-substitute-operation-for-newline-with-mac-difference), you'll need to add a `\` character to the end of each line in your `public.pem` file. Then run `./build.sh` to generate your `setLocalAdmin.py` script ready for deployment via your MDM tool of choice. This will reside in the project root, and also move your private key to `/webservice` for deployment.
3. Run `python3 -m pip install pycryptodome keyring` on the target machine. See 'Using the Script with Addigy' below on how to automate this nd the following 3 steps.
4. Deploy `setLocalAdmin.py` to the target machine
5. Configure a user account `localadmin` on the target
6. Run `python3 setLocalAdmin.py --initialPassword <initialPassword>` on the machine, replacing `<initialPassword>` with the password you've specified in step 5. See below on how to do this via an Addigy Command.
7. Set up running `python3 setLocalAdmin.py` as a recurring task at an interval of your choosing via your MDM tool
8. Copy the contents of `webservice/private.pem` in to a Password Management tool of your choice for safe keeping.

## The Web Service
We've written this using the bottle framework, which we find the easiest tool to quickly develop a microservice in. Inside `/webservice` you'll find a requirements.txt which you can use to setup a Python3 virtualenv. `wsgi.py` expects your `venv` directory be in the same directory. Copy the contents of `/webservice` to the path your web server is configured to serve from. Additionally, `wsgi.py` is written to look for a python3.7 `site-packages` folder, so if you're deploying to a different python version, you will want to modify the environment path set in that file.

Here's some sample Apache Configuration that should get you going. Note: we typically create a user account on our web server for each microservice. In this example the account name is `macospassword` and we also have `chmod +x /home/macospassword` so that Apache can search the path.
```
<VirtualHost>
    ServerName macospassword.internal.domain.com
    SSLEngineOn
    SSLCertificateFile /path/to/certificate
    SSLCertificateKeyFile /path/to/key
    SSLCertificateChainFile /path/to/chain

    WSGIDaemonProcess macOSPasswordDecrypter user=macospassword group=macospassword processes=1 threads=5 home=/home/macospassword
    WSGIScriptAlias /macospassword /home/macospassword/wsgi.py

    <Location />
            WSGIProcessGroup macOSPasswordDecrypter
            WSGIApplicationGroup %{RESOURCE}
    </Location>

    <Directory /home/macospassword>
            AddHandler wsgi-script .py
            Require all granted
    </Directory>
</VirtualHost>
```

## Using the Script with Addigy
To kick off the initial Password Rotation, you'll want to create a 'Script' like this:
```
#!/bin/bash
python3 -m pip install pycryptodome keyring
python3 - --initialPassword <Your_Policy_Defined_Password_Here> << EOF
#!/usr/bin/python3
<Contents of setLocalAdmin.py>
EOF 
```

You then want to deploy this using an Addigy 'Script' as a Maintenance Task on a weekly schedule to rotate the password:
```
#!/bin/bash
python3 << EOF
#!/usr/bin/python3
<Contents of setLocalAdmin.py>
EOF 
```

If you're using this on a mix of pre and post 10.15 / Catalina machines, you'll want to deploy Python3 and then adjust the first few lines of the above scripts to look something like:
```
if [ -e "/usr/local/bin/python3" ]; then
    path=/usr/local/bin/python3
else
    path=python3
fi
$path << EOF
```

## Addigy Facts and JAMF Extension Attributes
In `addigyFactScripts` you'll find two scripts that can be used as Custom Facts or Extension Attributes for monitoring of the target machine. One to retrieve the encrypted password, the other to let you know how long it has been since the password was last rotated. If the Encrypted Password script returns an empty string, it should be assumed there was an error in running the rotation process that needs manual intervention.

## Thanks
Some of the design of this project (namely storing the password in the System Keychain) came from the great [macOSLAPS project](https://github.com/joshua-d-miller/macOSLAPS). If you're running your macOS endpoints bound to AD, then check that out instead of this project.