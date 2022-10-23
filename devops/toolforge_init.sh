#!/bin/bash

toolforge-jobs run bootstrap-venv --command "cd $PWD && ./bootstrap_venv.sh" --image tf-python39 --wait
