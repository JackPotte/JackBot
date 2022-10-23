#!/bin/bash

cd JackBot
devops/update.sh

python3 core/pwb.py touch -lang:en -family:wikibooks -transcludes:"Template:Qr-em" -namespace:0
python3 core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en français" -namespace:0
python3 core/pwb.py touch -lang:fr -family:wiktionary -cat:"Singuliers manquants en anglais" -namespace:0

