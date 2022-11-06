#!/bin/bash

cd JackBot
devops/update_JackBot.sh

python3 core/pwb.py src/fr_wikiversity_format -r
