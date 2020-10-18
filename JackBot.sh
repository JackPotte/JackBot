#== Native scripts ==
#python core/pwb.py replace       -lang:commons -family:commons -file:articles_commons_txt "[[Category:PDF Wikibooks]]" "[[Category:English Wikibooks PDF]]"
#python core/pwb.py movepages     -lang:fr -family:wiktionary -pairsfile:"articles_fr_wiktionary.txt" -noredirect
#python core/pwb.py protect       -lang:fr -family:wiktionary -cat:"Élections de patrouilleurs" -summary:"Vote archivé" -move:sysop -edit:sysop
#python core/pwb.py delete        -lang:fr -family:wikiversity -file:"scripts/JackBot/articles_fr_wiktionary_txt"
#python core/pwb.py delete        -lang:en -family:wikibooks -cat:"Candidates for speedy deletion"
#python core/pwb.py touch         -lang:fr -family:wiktionary -cat:"Pluriels manquants en français" -namespace:0
#python core/pwb.py touch         -lang:fr -family:wiktionary -cat:"Singuliers manquants en anglais" -namespace:0
#python core/pwb.py touch         -lang:en -family:wikibooks -transcludes:"Template:Qr-em" -namespace:0
#python core/pwb.py login -all -pass

#=== Periodic tasks ===
#python core/pwb.py clean_sandbox -lang:fr -family:wiktionary  -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikibooks   -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikinews    -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikiversity -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikisource  -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikiquote   -always
#python core/pwb.py clean_sandbox -lang:fr -family:wikivoyage  -always
##python core/pwb.py clean_sandbox -lang:fr -family:wikipedia   -always
#python core/pwb.py clean_sandbox -lang:en -family:wikibooks   -always
##python core/pwb.py clean_sandbox -lang:en -family:wikiquote   -always

#python core/pwb.py redirect double -always -family:wikipedia -lang:fr
#python core/pwb.py redirect double -always -family:wikipedia -lang:pl
#python core/pwb.py redirect double -always -family:wikipedia -lang:se
#python core/pwb.py redirect double -always -family:wikipedia -lang:ta

#python core/pwb.py redirect double -always -family:wiktionary -lang:de
#python core/pwb.py redirect double -always -family:wiktionary -lang:en
#python core/pwb.py redirect double -always -family:wiktionary -lang:es
#python core/pwb.py redirect double -always -family:wiktionary -lang:fr
#python core/pwb.py redirect double -always -family:wiktionary -lang:it
#python core/pwb.py redirect double -always -family:wiktionary -lang:my
#python core/pwb.py redirect double -always -family:wiktionary -lang:pt
#python core/pwb.py redirect double -always -family:wiktionary -lang:ru
#python core/pwb.py redirect double -always -family:wiktionary -lang:sv
#python core/pwb.py redirect double -always -family:wiktionary -lang:zh

#python core/pwb.py redirect double -always -family:wikiversity -lang:en
#python core/pwb.py redirect double -always -family:wikiversity -lang:fr
#python core/pwb.py redirect double -always -family:wikibooks -lang:en
#python core/pwb.py redirect double -always -family:wikibooks -lang:es
#python core/pwb.py redirect double -always -family:wikibooks -lang:fr
##python core/pwb.py redirect double -always -family:wikisource -lang:en
#python core/pwb.py redirect double -always -family:wikisource -lang:fr
#python core/pwb.py redirect double -always -family:wikiquote -lang:fr
#python core/pwb.py redirect double -always -family:wikiquote -lang:en
#python core/pwb.py redirect double -always -family:wikinews -lang:fr
#python core/pwb.py redirect double -always -family:wikivoyage -lang:de
#python core/pwb.py redirect double -always -family:wikivoyage -lang:fr

#python core/pwb.py redirect broken -lang:fr -family:wiktionary -always
#python core/pwb.py redirect broken -lang:fr -family:wikiversity -always
##python core/pwb.py redirect broken -lang:fr -family:wikibooks -always # pb du livre de photos


#== Maintained scripts ==
#python core/pwb.py src/fr_wikinews_to_wikipedia
#python core/pwb.py src/fr_wikiquote_count_quotes -family:wikiquote -output:"User:JackBot/statistiques" -outputquotes:"Template:NUMBEROFQUOTES"


#== Homemade scripts ==
#python core/pwb.py src/fr_wikibooks_format -cat
#python core/pwb.py src/fr_wikinews_format -cat
#python core/pwb.py src/fr_wikiquote_format -cat
#python core/pwb.py src/fr_wikiversity_format -cat
#python core/pwb.py src/fr_wikivoyage_format -cat
#python core/pwb.py src/en_wikiquote_format -cat
#python core/pwb.py src/en_wikiversity_format -cat
#python core/pwb.py src/fr_wikipedia_format -cat
#python core/pwb.py src/en_wikibooks_format -cat
#python core/pwb.py src/wiktionary/en_wiktionary_format -cat
#python core/pwb.py src/wiktionary/fr_wiktionary_format -cat
#python core/pwb.py src/wiktionary/fr_wiktionary_format_py -u Escarbot revocation 1000

#=== Current daily global operations ===
python core/pwb.py src/en_wikibooks_format -nocat
python core/pwb.py src/fr_wikibooks_format -nocat
python core/pwb.py src/fr_wikiversity_format -nocat
python core/pwb.py src/fr_wikipedia_format
python core/pwb.py src/wiktionary/fr_wiktionary_archive
python core/pwb.py src/wiktionary/fr_wiktionary_create_inflexions
python core/pwb.py src/wiktionary/fr_wiktionary_format
python core/pwb.py src/wiktionary/fr_wiktionary_import_from_commons

#TODO: updateDumps_sh (by cron)
