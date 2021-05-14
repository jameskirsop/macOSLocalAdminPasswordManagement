#!/bin/bash
TENORELEVEN="$(sw_vers -productVersion | awk -F. '{ print $1; }')"
if [[ $TENORELEVEN -eq 10 ]]; then
    MACOS_VER="$(sw_vers -productVersion | awk -F. '{ print $1"."$2; }')"
else
    MACOS_VER=$TENORELEVEN
fi

ARCH="$(arch)"
PEX="venv_macOS${MACOS_VER}_${ARCH}.pex"

pex --python=/usr/local/bin/managed_python3 --python-shebang=/usr/local/bin/managed_python3 -r pexEnvironments/requirements.txt -o pexEnvironments/"$PEX"