#!/bin/bash

cd JackBot
devops/update_JackBot.sh

python3 core/pwb.py src/en_wikibooks_add_authors_and_contributors.py
