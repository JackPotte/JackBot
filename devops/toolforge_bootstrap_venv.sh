#!/bin/bash
# Used by toolforge_init.sh

# use bash strict mode
set -euo pipefail

rm -rf pyvenv

python3 -m venv pyvenv

source pyvenv/bin/activate

pip install -U pip wheel

pip install -r JackBot/requirements.txt
