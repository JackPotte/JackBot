python redirect.py double -always -family:wikipedia -lang:fr
python redirect.py double -always -family:wikipedia -lang:pl
python redirect.py double -always -family:wikipedia -lang:se
python redirect.py double -always -family:wikipedia -lang:tr
python redirect.py double -always -family:wikipedia -lang:ta
python redirect.py double -always -family:wiktionary -lang:de
python redirect.py double -always -family:wiktionary -lang:en
python redirect.py double -always -family:wiktionary -lang:es
python redirect.py double -always -family:wiktionary -lang:fr
python redirect.py double -always -family:wiktionary -lang:it
python redirect.py double -always -family:wiktionary -lang:my
python redirect.py double -always -family:wiktionary -lang:pt
python redirect.py double -always -family:wiktionary -lang:ru
python redirect.py double -always -family:wiktionary -lang:sv
python redirect.py double -always -family:wiktionary -lang:zh
python redirect.py double -always -family:wikiversity -lang:en
python redirect.py double -always -family:wikiversity -lang:fr
python redirect.py double -always -family:wikibooks -lang:en
python redirect.py double -always -family:wikibooks -lang:fr
rem python redirect.py double -always -family:wikisource -lang:en
python redirect.py double -always -family:wikisource -lang:fr
python redirect.py double -always -family:wikiquote -lang:fr
python redirect.py double -always -family:wikiquote -lang:en
python redirect.py double -always -family:wikinews -lang:fr
python redirect.py double -always -family:wikivoyage -lang:de
python redirect.py double -always -family:wikivoyage -lang:fr
python redirect.py double -always -family:wikivoyage -lang:he

python redirect.py broken -lang:fr -family:wiktionary -always
python redirect.py broken -lang:fr -family:wikiversity -always
rem python redirect.py broken -lang:fr -family:wikibooks -always # pb du livre de photos

python clean_sandbox.py -lang:fr -family:wikiversity
python clean_sandbox.py -lang:fr -family:wikibooks
python clean_sandbox.py -lang:fr -family:wiktionary
python fr.n.bas.py -lang:fr -family:wikinews

rem python fr.w.archive.py # bug ?
python fr.wikt.archive.py

python fr.wikt.RemiseEnForme.py
python fr.w.formatage.py
pause