#!/bin/bash

set -euo pipefail

python3 -m venv pyenv

source pyenv/bin/activate

pip install -U pip wheel

pip install -r JackBot/requirements.txt

