#!/bin/bash

cd JackBot
devops/update_JackBot.sh

$python core/pwb.py clean_sandbox.py -q -lang:fr -family:wiktionary
$python core/pwb.py clean_sandbox.py -q -lang:fr -family:wikibooks
$python core/pwb.py clean_sandbox.py -q -lang:en -family:wikibooks
$python core/pwb.py clean_sandbox.py -q -lang:fr -family:wikiversity
#$python core/pwb.py clean_sandbox.py -q -lang:en -family:wikiversity
$python core/pwb.py clean_sandbox.py -q -lang:fr -family:wikiquote
#$python core/pwb.py clean_sandbox.py -q -lang:en -family:wikiquote
#$python core/pwb.py clean_sandbox.py -q -lang:fr -family:wikivoyage
$python core/pwb.py clean_sandbox.py -q -lang:fr -family:wikisource

#$python core/pwb.py src/wiktionary/fr_wiktionary_archive.py -q
$python core/pwb.py src/TalkArchiver -family:wiktionary
$python core/pwb.py src/TalkArchiver -family:wikisource
$python core/pwb.py src/TalkArchiver -family:wiktionary -p:'Projet:Gadget de création d’entrées/Suggestions'
