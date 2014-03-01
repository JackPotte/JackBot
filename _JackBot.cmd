python redirect.py double -always -family:wiktionary -lang:fr
python redirect.py double -always -family:wikipedia -lang:fr
python redirect.py double -always -family:wikibooks -lang:fr
python redirect.py double -always -family:wikiversity -lang:fr
python redirect.py double -always -family:wikinews -lang:fr
python redirect.py double -always -family:wikisource -lang:fr
python redirect.py double -always -family:wikiquote -lang:fr

python redirect.py double -always -family:wiktionary -lang:en
rem python redirect.py double -always -family:wikipedia -lang:en
python redirect.py double -always -family:wikibooks -lang:en
python redirect.py double -always -family:wikiversity -lang:en
rem python redirect.py double -always -family:wikinews -lang:en
rem python redirect.py double -always -family:wikisource -lang:en
python redirect.py double -always -family:wikiquote -lang:en

python redirect.py double -always -family:wiktionary -lang:ar
python redirect.py double -always -family:wiktionary -lang:de
python redirect.py double -always -family:wiktionary -lang:el
python redirect.py double -always -family:wiktionary -lang:es
python redirect.py double -always -family:wiktionary -lang:gl
python redirect.py double -always -family:wiktionary -lang:he
python redirect.py double -always -family:wiktionary -lang:hi
python redirect.py double -always -family:wiktionary -lang:id
python redirect.py double -always -family:wiktionary -lang:ja
python redirect.py double -always -family:wiktionary -lang:la
python redirect.py double -always -family:wiktionary -lang:pt
python redirect.py double -always -family:wiktionary -lang:ru
python redirect.py double -always -family:wiktionary -lang:tr
python redirect.py double -always -family:wiktionary -lang:vi
python redirect.py double -always -family:wiktionary -lang:zh

python redirect.py broken -lang:fr -family:wiktionary -always
python redirect.py broken -lang:fr -family:wikiversity -always

python clean_sandbox.py -lang:fr -family:wikiversity
python clean_sandbox.py -lang:fr -family:wikibooks
python clean_sandbox.py -lang:fr -family:wiktionary
python fr.n.bas.py -lang:fr -family:wikinews

python fr.w.archive.py
python fr.wikt.archive.py
python fr.wikt.RemiseEnForme.py

pause