from wikipedia import *
from pageimport import *
def main():
    # Defing what page to load..
    pagetoload = 'Ict@innovation: Free your IT Business in Africa/fr/1'
    site = wikipedia.getSite(u'fr',u'wikibooks')
    importerbot = Importer(site) # Inizializing
    importerbot.Import(pagetoload, prompt = True, project = u'en')
try:
    main()
finally:
    wikipedia.stopme()