#!/bin/bash

cd JackBot
devops/update.sh

python3 core/pwb.py src/fr_wikiquote_count_quotes.py -family:wikiquote -output:"User:JackBot/statistiques" -outputquotes:"Template:NUMBEROFQUOTES"

