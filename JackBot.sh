# Native
#python core/pwb.py replace       -lang:commons -family:commons -file:articles_commons.txt "[[Category:PDF Wikibooks]]" "[[Category:English Wikibooks PDF]]"
#python core/pwb.py touch         -lang:fr -family:wiktionary -cat:"Singuliers manquants en anglais"
#python core/pwb.py movepages     -lang:fr -family:wiktionary -pairs:"articles_fr_wiktionary.txt" -noredirect -pairs
#python core/pwb.py protect       -lang:fr -family:wiktionary -cat:"Élections de patrouilleurs" -summary:"Vote archivé" -move:sysop -edit:sysop
#python core/pwb.py delete        -lang:fr -family:wikiversity -file:"scripts/JackBot/articles_fr_wiktionary.txt"
python core/pwb.py clean_sandbox -lang:fr -family:wiktionary  -always
python core/pwb.py clean_sandbox -lang:fr -family:wikibooks   -always
python core/pwb.py clean_sandbox -lang:fr -family:wikinews    -always
python core/pwb.py clean_sandbox -lang:fr -family:wikiversity -always
python core/pwb.py clean_sandbox -lang:fr -family:wikisource  -always
python core/pwb.py clean_sandbox -lang:fr -family:wikiquote   -always
python core/pwb.py clean_sandbox -lang:fr -family:wikivoyage  -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikipedia   -always

# Homemade
#python core/pwb.py src/fr.wiktionary.format
#python core/pwb.py src/fr.wikipedia.format
#python core/pwb.py src/fr.wikinews.2wikipedia
#python core/pwb.py src/fr.wikiquote.count-quotes -family:wikiquote -output:"User:JackBot/statistiques" -outputarticles:"Template:NUMBEROFQARTICLES" -outputquotes:"Template:NUMBEROFQUOTES"

