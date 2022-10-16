./update.sh
cd JackBot
python3 core/pwb.py src/fr_wikibooks_format -nocat
python3 core/pwb.py src/en_wikibooks_format -nocat
python3 core/pwb.py src/fr_wikiversity_format -nocat

