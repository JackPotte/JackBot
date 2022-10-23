#!/bin/bash

cd JackBot
devops/update.sh

python3 core/pwb.py src/fr_wikipedia_format -cat

