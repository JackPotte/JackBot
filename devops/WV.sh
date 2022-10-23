#!/bin/bash

cd JackBot
devops/update.sh

python3 core/pwb.py src/fr_wikiversity_format -r
