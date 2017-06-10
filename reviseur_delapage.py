#!/usr/bin/python
# -*- coding: latin-1 -*-
# Pour Python 3, remplacez la ligne ci-dessous par import urllib.request, re
import urllib, re       # import des modules a partir de la bibliotheque d'instructions de base, 
nom_de_page = "Accueil" #             'urllib' pour URL library et 're' pour regular expression.

url = "http://fr.wikipedia.org/w/api.php?action=query&prop=info|revisions&titles=%s&format=xml" % nom_de_page
# affichage
# Python 3 : page = urllib.request.urlopen(url) 
page = urllib.urlopen(url) 
# Python 3 : infos = str(page.read(), 'utf_8')
infos = page.read()        # lit le resultat de la requete a l'url ci-dessus
page.close()
print "Les informations demandees concernant", nom_de_page, "sont les suivantes, en XML :\n\n", infos  # Rajoutez des parenthèses pour Python 3 !

# extraction
print "\n...recherche l'expression rationnelle..."  # Rajoutez des parenthèses pour Python 3 !
reviseur= re.findall(' user="(.*?)" ',infos) # recherche l'expression rationnelle
print "\nDernier reviseur : ",reviseur   # Rajoutez des parenthèses pour Python 3 !