#!/bin/bash

cd JackBot
devops/update_JackBot.sh
if [ $HOME = "/data/project/jackbot" ]
  then python=../pyvenv/bin/python
else
  python=python3
fi

$python core/pwb.py redirect.py double -always -family:wikipedia -lang:fr
$python core/pwb.py redirect.py double -always -family:wikipedia -lang:pl
$python core/pwb.py redirect.py double -always -family:wikipedia -lang:se
$python core/pwb.py redirect.py double -always -family:wikipedia -lang:ta

$python core/pwb.py redirect.py double -always -family:wiktionary -lang:de
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:en
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:es
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:fr
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:it
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:my
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:pt
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:ru
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:sv
$python core/pwb.py redirect.py double -always -family:wiktionary -lang:zh

$python core/pwb.py redirect.py double -always -family:wikiversity -lang:en
$python core/pwb.py redirect.py double -always -family:wikiversity -lang:fr
$python core/pwb.py redirect.py double -always -family:wikibooks -lang:en
$python core/pwb.py redirect.py double -always -family:wikibooks -lang:es
$python core/pwb.py redirect.py double -always -family:wikibooks -lang:fr
#$python core/pwb.py redirect.py double -always -family:wikisource -lang:en
$python core/pwb.py redirect.py double -always -family:wikisource -lang:fr
$python core/pwb.py redirect.py double -always -family:wikiquote -lang:fr
$python core/pwb.py redirect.py double -always -family:wikiquote -lang:en
$python core/pwb.py redirect.py double -always -family:wikivoyage -lang:de
$python core/pwb.py redirect.py double -always -family:wikivoyage -lang:fr

$python core/pwb.py redirect.py broken -lang:fr -family:wiktionary -always
$python core/pwb.py redirect.py broken -lang:fr -family:wikiversity -always
#$python core/pwb.py redirect.py broken -lang:fr -family:wikibooks -always # pb du livre de photos

