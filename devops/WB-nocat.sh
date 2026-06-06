#!/bin/bash

cd JackBot
devops/update_JackBot.sh

$python core/pwb.py src/fr_wikibooks_format -nocat
$python core/pwb.py src/en_wikibooks_format -nocat
$python core/pwb.py src/fr_wikiversity_format -nocat

