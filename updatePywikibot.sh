rm -Rf core
wget https://tools.wmflabs.org/pywikibot/core_stable.zip
unzip core_stable.zip
mv core_stable core
rm core_stable.zip
rm -Rf core/.git

cd core/scripts/i18n
git pull
rm -Rf .git
