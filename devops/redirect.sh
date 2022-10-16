cd JackBot

python3 core/pwb.py redirect.py double -always -family:wikipedia -lang:fr
python3 core/pwb.py redirect.py double -always -family:wikipedia -lang:pl
python3 core/pwb.py redirect.py double -always -family:wikipedia -lang:se
python3 core/pwb.py redirect.py double -always -family:wikipedia -lang:ta

python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:de
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:en
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:es
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:fr
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:it
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:my
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:pt
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:ru
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:sv
python3 core/pwb.py redirect.py double -always -family:wiktionary -lang:zh

python3 core/pwb.py redirect.py double -always -family:wikiversity -lang:en
python3 core/pwb.py redirect.py double -always -family:wikiversity -lang:fr
python3 core/pwb.py redirect.py double -always -family:wikibooks -lang:en
python3 core/pwb.py redirect.py double -always -family:wikibooks -lang:es
python3 core/pwb.py redirect.py double -always -family:wikibooks -lang:fr
#python3 core/pwb.py redirect.py double -always -family:wikisource -lang:en
python3 core/pwb.py redirect.py double -always -family:wikisource -lang:fr
python3 core/pwb.py redirect.py double -always -family:wikiquote -lang:fr
python3 core/pwb.py redirect.py double -always -family:wikiquote -lang:en
python3 core/pwb.py redirect.py double -always -family:wikinews -lang:fr
python3 core/pwb.py redirect.py double -always -family:wikivoyage -lang:de
python3 core/pwb.py redirect.py double -always -family:wikivoyage -lang:fr

python3 core/pwb.py redirect.py broken -lang:fr -family:wiktionary -always
python3 core/pwb.py redirect.py broken -lang:fr -family:wikiversity -always
#python3 core/pwb.py redirect.py broken -lang:fr -family:wikibooks -always # pb du livre de photos

