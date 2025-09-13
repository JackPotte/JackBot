#!/bin/bash

cd JackBot
devops/update_JackBot.sh

python3 core/pwb.py clean_sandbox.py -q -lang:fr -family:wiktionary
python3 core/pwb.py clean_sandbox.py -q -lang:fr -family:wikibooks
python3 core/pwb.py clean_sandbox.py -q -lang:en -family:wikibooks
python3 core/pwb.py clean_sandbox.py -q -lang:fr -family:wikiversity
#python3 core/pwb.py clean_sandbox.py -q -lang:en -family:wikiversity
python3 core/pwb.py clean_sandbox.py -q -lang:fr -family:wikinews
python3 core/pwb.py clean_sandbox.py -q -lang:fr -family:wikiquote
#python3 core/pwb.py clean_sandbox.py -q -lang:en -family:wikiquote
#python3 core/pwb.py clean_sandbox.py -q -lang:fr -family:wikivoyage
python3 core/pwb.py clean_sandbox.py -q -lang:fr -family:wikisource

#python3 core/pwb.py src/wiktionary/fr_wiktionary_archive.py -q
python3 core/pwb.py src/TalkArchiver -family:wiktionary
python3 core/pwb.py src/TalkArchiver -family:wikisource
python3 core/pwb.py src/TalkArchiver -family:wiktionary -p:'Projet:Gadget de création d’entrées/Suggestions'
