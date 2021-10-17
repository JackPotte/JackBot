#!/bin/bash

rm -Rf core
wget https://tools.wmflabs.org/pywikibot/core_stable.zip
unzip core_stable.zip
mv core_stable core
rm core_stable.zip
rm -Rf core/.git
pip install -r requirements.txt

cd core/scripts/i18n
git pull
#rm -Rf .git

pip install i18n
pip install regex
pip install requests

if [ ! -e 'user-config.py' ]
  then cp user-config.py.dist user-config.py
fi
