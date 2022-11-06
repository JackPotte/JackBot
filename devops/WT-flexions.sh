#!/bin/bash

cd JackBot
devops/update_JackBot.sh

python3 core/pwb.py src/wiktionary/fr_wiktionary_create_inflexions

python3 core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en français"
python3 core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en italien"

