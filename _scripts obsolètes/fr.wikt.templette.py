# Ce robot remplace un modèle par un autre en conservant un paramètre
#!/usr/bin/env python

# Déclaration
language = "fr"
family = "wiktionary"
mynick = "JackBot"

# Importation des modules
import os
from wikipedia import *
site = getSite(language,family)
templette1 = "{{cs-conj-perf-it|rad="
templette2 = "}}"
template1 = "{{cs-conj-perf-i|rad="
template2 = "||i}}"
texte = "[[WT:BR]]"

# Lecture du fichier articles_list.txt (au même format que pour replace.py)
def lecture(source):
    PagesHS = open(source, 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': break
		modification(PageHS)
    PagesHS.close()

	
# Modification du wiki
def modification(PageHS):
  page = Page(site,PageHS)
  PageTemp = page.get()
  PageEnd = ""
  position = 0
  while position < len(PageTemp):
  	  position = PageTemp.find(templette1)
	  if position < 0:
	    break
	  else:
	    PageEnd = PageEnd + PageTemp[0:position]
	    PageTemp = PageTemp[position:len(PageTemp)]
	    position = PageTemp.find(templette2)
	    radical = PageTemp[len(templette1):position]
	    PageEnd = PageEnd + template1 + radical + template2
	    PageTemp = PageTemp[position+len(templette2):len(PageTemp)]
  PageEnd = PageEnd + PageTemp[0:len(PageTemp)]
  #print(PageEnd)
  page.put(PageEnd, texte)
  
# Lancement
HS = lecture('articles_list.txt')
# print HS
raw_input("Jackpot")
