#!/bin/bash

cd JackBot
devops/update_JackBot.sh
if [ $HOME = "/data/project/jackbot" ]
  then python=../pyvenv/bin/python
else
  python=python3
fi

$python core/pwb.py src/fr_wikiquote_count_quotes.py -family:wikiquote -output:"User:JackBot/statistiques" -outputquotes:"Template:NUMBEROFQUOTES"

