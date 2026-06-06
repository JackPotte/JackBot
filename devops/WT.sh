#!/bin/bash

cd JackBot
devops/update_JackBot.sh
if [ $HOME = "/data/project/jackbot" ]
  then python=../pyvenv/bin/python
else
  python=python3
fi

$python core/pwb.py src/wiktionary/fr_wiktionary_format
