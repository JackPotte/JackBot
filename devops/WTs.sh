#!/bin/bash

cd JackBot
devops/update_JackBot.sh

$python core/pwb.py src/wiktionary/fr_wiktionary_format -s "insource:/ \[\[Catégorie:/"


