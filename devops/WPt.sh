#!/bin/bash

cd JackBot
devops/update_JackBot.sh

$python core/pwb.py src/fr_wikipedia_format -txt

