#!/bin/bash

cd JackBot
devops/update_JackBot.sh
if [ $HOME = "/data/project/jackbot" ]
  then python=../pyvenv/bin/python
else
  python=python3
fi

$python core/pwb.py touch -lang:fr -family:wikibooks -page:Accueil -purge
$python core/pwb.py touch -lang:en -family:wikibooks -transcludes:"Template:Qr-em" -namespace:0

$python core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en français" -namespace:0
$python core/pwb.py touch -lang:fr -family:wiktionary -cat:"Singuliers manquants en anglais" -namespace:0
