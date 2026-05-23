#!/bin/bash

toolforge jobs list

#toolforge jobs run commons --command "$HOME/JackBot/devops/WT-Commons.sh" --image python3.11 --schedule "0 7 * * 0" --emails onfailure

toolforge jobs delete redirect; toolforge jobs run redirect --command "$HOME/JackBot/devops/redirect.sh" --image python3.11 --schedule "0 4 * * *" --emails onfailure
toolforge jobs delete talks-archive; toolforge jobs run talks-archive --command "$HOME/JackBot/devops/talks-archive.sh" --image python3.11 --schedule "0 */12 * * *" --emails onfailure
toolforge jobs delete touch; toolforge jobs run touch --command "$HOME/JackBot/devops/touch.sh" --image python3.11 --schedule "1 23 * * *" --emails onfailure
toolforge jobs delete wikibooks; toolforge jobs run wikibooks --command "$HOME/JackBot/devops/WB-nocat.sh" --image python3.11 --schedule "0 1 * * *" --emails onfailure
toolforge jobs delete wikipedia; toolforge jobs run wikipedia --command "$HOME/JackBot/devops/WP.sh" --image python3.11 --schedule "0 2 * * *" --emails onfailure
toolforge jobs delete wikiquote; toolforge jobs run wikiquote --command "$HOME/JackBot/devops/WQ.sh" --image python3.11 --schedule "0 6 * * *" --emails onfailure
toolforge jobs delete wikt-inflexions; toolforge jobs run wikt-inflexions --command "$HOME/JackBot/devops/WT-flexions.sh" --image python3.11 --schedule "0 3 * * *" --emails onfailure
toolforge jobs delete wiktionary; toolforge jobs run wiktionary --command "$HOME/JackBot/devops/WT.sh" --image python3.11 --schedule "0 0 * * *" --emails onfailure
