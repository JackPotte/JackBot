#!/bin/bash

# toolforge-jobs delete touch
toolforge-jobs run wiktionary --command "$HOME/JackBot/devops/WT.sh" --image tf-python39 --schedule "0 0 * * *" --emails onfailure
toolforge-jobs run wikt-inflexions --command "$HOME/JackBot/devops/WT-flexions.sh" --image tf-python39 --schedule "0 3 * * *" --emails onfailure
toolforge-jobs run wikipedia --command "$HOME/JackBot/devops/WP.sh" --image tf-python39 --schedule "0 2 * * *" --emails onfailure
toolforge-jobs run wikinews --command "$HOME/JackBot/devops/WP-WN.sh" --image tf-python39 --schedule "0 */12 * * *" --emails onfailure
toolforge-jobs run wikibooks --command "$HOME/JackBot/devops/WB-nocat.sh" --image tf-python39 --schedule "0 1 * * *" --emails onfailure
toolforge-jobs run wikiquote --command "$HOME/JackBot/devops/WQ.sh" --image tf-python39 --schedule "0 6 * * *" --emails onfailure
toolforge-jobs run commons --command "$HOME/JackBot/devops/WT-Commons.sh" --image tf-python39 --schedule "0 7 * * 0" --emails onfailure

toolforge-jobs run talks-archive --command "$HOME/JackBot/devops/talks-archive.sh" --image tf-python39 --schedule "0 */12 * * *" --emails onfailure
toolforge-jobs run redirect --command "$HOME/JackBot/devops/redirect.sh" --image tf-python39 --schedule "0 4 * * *" --emails onfailure
toolforge-jobs run touch --command "$HOME/JackBot/devops/touch.sh" --image tf-python39 --schedule "1 23 * * *" --emails onfailure
