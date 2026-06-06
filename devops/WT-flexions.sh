#!/bin/bash

cd JackBot
devops/update_JackBot.sh
if [ $HOME = "/data/project/jackbot" ]
  then python=../pyvenv/bin/python
else
  python=python3
fi

$python core/pwb.py src/wiktionary/fr_wiktionary_create_inflexions

$python core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en français"
$python core/pwb.py touch -lang:fr -family:wiktionary -cat:"Pluriels manquants en italien"

