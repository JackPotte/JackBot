#!/bin/bash

cd JackBot
git stash
git pull -f

if [ $HOME = "/data/project/jackbot" ]
  then python=../pyvenv/bin/python
else
  python=python3
fi
