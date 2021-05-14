# macOSLocalAdminPasswordManagement

This project has been written to allow for deployment of a unique 'localadmin' account password on macOS 11 and newer and rotation of that password. It uses RSA public/private key encryption to allow secure escrow of the encrypted password to an MDM platform and has a simple micro web service that can be deployed via WSGI to allow password decryption.

_This script will work on 10.15, but will not grant a SecureToken because Dialog requires macOS 11. Use the `--noGrantSecureToken` flag._

## Requirements
- [Dialog](https://github.com/bartreardon/dialog-public) installed on the target machine, if you wish to use the script for enabling a SecureToken on the localadmin account. See further notes on how we use Dialog below.
- [managed_python3](https://github.com/macadmins/python)

## Instructions for Deployment to the Target Machine
1. Run `./buildDeployment.sh` to generate your RSA Keys and build the deployment script. You will be prompted for an RSA Passphrase serveral times to create the Private key and then an unencrypted copy for the webservice. The built `setLocalAdmin.py` will reside in your project root ready for deployment via your MDM tool of choice (see below for use with Addigy). Your unencrypted private key will also be moved to `/webservice` for deployment.
2. Copy the contents of `webservice/private.pem` in to a Password Management tool of your choice for safe keeping so that you will be able to decrypt passwords if something happens to your webserver.
3. Deploy [managed_python3](https://github.com/macadmins/python) along with the pex virtualenv's (venv_macOS-release-arch) to the machine
4. Symlink /usr/local/bin/managed_py3env to the appropriate pex file for the system. `deployPexEnv.sh` has a sample bash script that can do this for you as part of the `managed_python3` installation if you're using Addigy as your MDM tool.
5. Deploy Dialog inline with the recommendations found below.
6. Deploy an administrative account with username 'localadmin' and a complex password of your choosing via your MDM tool


### Flags for setLocalAdmin.py
`--initialPassword`
Pass the password that you set via your MDM tool for the localadmin account. This only needs to be passed for the first run, after that the flag is no longer needed (unless, of course you reset the password manually)

`--noGrantSecureToken`
Useful for 10.15 or older machines where this script does not support prompting the user with an interactive dialog to get credentials to grant a Secure Token to the localadmin user. 


### Dialog
In addition to Dialog being installed, we expect a banner image file to be located at `/Library/Application\ Support/Dialog/dialog_banner_small.png`. The dimensions for this image are 1417x205. **Without this file, Dialog will fail to display the user prompt for the Grant Secure Token action.**


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
To kick off the initial Password Rotation, you'll want to create a 'Saved Script' like this:
```
#!/bin/bash
/usr/local/bin/managed_py3env - --initialPassword <Your_Policy_Defined_Password_Here> << EOF
<Contents of setLocalAdmin.py>
EOF 
```

You then want to deploy this using an Addigy 'Script' as a Maintenance Task on a weekly schedule to rotate the password:
```
#!/bin/bash
/usr/local/bin/managed_py3env << EOF
<Contents of setLocalAdmin.py>
EOF 
```

## Addigy Facts and JAMF Extension Attributes
In `addigyFactScripts` you'll find two scripts that can be used as Custom Facts or Extension Attributes for monitoring of the target machine. One to retrieve the encrypted password, the other to let you know how long it has been since the password was last rotated. If the Encrypted Password script returns an empty string, it should be assumed there was an error in running the rotation process that needs manual intervention.

## Pex Environments
We've pre-built Pex environments based on the contents of `pexEnvironments/requirements.txt` for 10.15 and 11. If you have trouble with them use `pexBuild.sh` to build your own. You'll need `managed_python3` and `pex` (installed via pip) on the system to build. Note that you need to build on each OS and Architechture (ARM/Intel) that you wish to deploy to.

## Thanks
Some of the design of this project (namely storing the password in the System Keychain) came from the great [macOSLAPS project](https://github.com/joshua-d-miller/macOSLAPS). If you're running your macOS endpoints bound to AD, then check that out instead of this project.

Thanks also to [@bartreardon](http://github.com/bartreardon) for adding some features to Dialog and letting me bug him with questions on the MacAdmins Slack.