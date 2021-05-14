#!/bin/bash
PACKAGE_NAME="Managed Python (3.9.1.04202021212856)"

TENORELEVEN="$(sw_vers -productVersion | awk -F. '{ print $1; }')"
if [[ $TENORELEVEN -eq 10 ]]; then
    MACOS_VER="$(sw_vers -productVersion | awk -F. '{ print $1"."$2; }')"
else
    MACOS_VER=$TENORELEVEN
fi

ARCH="$(arch)"
PEX="venv_macOS${MACOS_VER}_${ARCH}.pex"

ln -s /Library/Addigy/ansible/packages/"$PACKAGE_NAME"/"$PEX" /usr/local/bin/managed_py3env
chmod a+x /usr/local/bin/managed_py3env