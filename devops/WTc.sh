#!/bin/bash

cd JackBot
devops/update_JackBot.sh

python3 core/pwb.py src/wiktionary/fr_wiktionary_format -cat

