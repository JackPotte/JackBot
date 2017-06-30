# Native
#python core/pwb.py replace      -lang:commons -family:commons -file:articles_commons.txt "[[Category:PDF Wikibooks]]" "[[Category:English Wikibooks PDF]]"
#python core/pwb.py touch        -lang:fr -family:wiktionary -cat:"Singuliers manquants en anglais"
#python core/pwb.py movepages    -lang:fr -family:wiktionary -pairs:"articles_fr_wiktionary.txt" -noredirect -pairs
#python core/pwb.py protect      -lang:fr -family:wiktionary -cat:"Élections de patrouilleurs" -summary:"Vote archivé" -move:sysop -edit:sysop
#python core/pwb.py delete       -lang:fr -family:wikiversity -file:"scripts/JackBot/articles_fr_wiktionary.txt"

# Homemade
python core/pwb.py src/fr.wiktionary.format
#python core/pwb.py src/fr.wikipedia.format
#python core/pwb.py src/fr.wikinews.2wikipedia
#python core/pwb.py src/fr.wikiquote.count-quotes
