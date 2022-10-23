#!/bin/bash

cd JackBot
devops/update.sh

python3 core/pwb.py src/wiktionary/fr_wiktionary_import_from_commons.py -cat

