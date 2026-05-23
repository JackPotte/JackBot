#!/bin/bash
# After: toolforge webservice python3.11 shell

toolforge jobs run bootstrap-venv --command "cd $PWD && ./JackBot/devops/toolforge_bootstrap_venv.sh" --image python3.11 --wait
