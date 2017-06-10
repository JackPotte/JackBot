#!/usr/bin/env python
# coding: utf-8
# This script creates the French entries from the French Wiktionary, which are attested by at least another online dictionary

# Importing modules
from wikipedia import *
import urllib, config, re, sys, codecs

# Declaring all global values
language = "fr"
family = "wiktionary"
mynick = "JackBot"
site = getSite(language,family)
sitefr = getSite("en",family)
source = "articles_list.txt"
template = "\n=={{langue|en}}==\n{{-flex-verb-}}\n\'''{{subst:PAGENAME}}\'''\n# {{inflection of|"
msg= u'Importations from [[fr:|fr.wiktionary]] attested by another online dictionary'

# Word existence checking
'''
word = raw_input("Please enter a French verb form.\n")
onlinedict = urllib.urlopen("http://www.larousse.fr/dictionnaires/rechercher/" + word,"utf-8").read()
existence = onlinedict.find("v.")
if existence > 0:
	print (word + " is a French verb form\n")
else:
	print (word + " is not a French verb form\n")
'''	

word = "testons"
onlinedict = urllib.urlopen("http://www.larousse.fr/dictionnaires/rechercher/" + word,"utf-8").read()
existence = onlinedict.find("v.")
'''
def lecture(source):
    PagesHS = open(source, 'r')
    while 1:
		PageHS = PagesHS.readline()
		fin = PageHS.find("\t")
		PageHS = PageHS[0:fin]
		if PageHS == '': break
		modification(PageHS)
    PagesHS.close()
'''

# Wiki importation
def modification(PageHS):
	if existence > 0:
		page = Page(site,PageHS)
		PageEnd = page.get()
		pagefr = Page(sitefr,PageHS)
		PageTemp = pagefr.get()
		pagetest = Page(site,"User:JackBot/test")
		Test = pagetest.get()
		position = PageTemp.find("{{-flex-verb-")
		PageTemp = PageTemp[position:len(PageTemp)]
		position = PageTemp.find("]].")
		if position < 0:
			position = PageTemp.find("]]'''.")
		PageTemp = PageTemp[0:position]
		while position > 0:
			position = PageTemp.find("[[")
			PageTemp = PageTemp[position+1:len(PageTemp)]
		PageTemp = PageTemp[1:len(PageTemp)]
		PageEnd = template + PageTemp + "||inflection|lang=fr}}\n"
		pagetest.put(PageEnd, msg)
		
modification(word)
'''
include = False
titlestart = u"<<<"
titleend = u">>>"
search_string = u""
force = False
append = "False"
notitle = True

def findpage(t):
    search_string = titlestart + "(.*?)" + titleend
    try:
        location = re.search(starttext+"([^\Z]*?)"+endtext,t)
        if include:
            contents = location.group()
        else:
            contents = location.group(1)
    except AttributeError:
        print 'Start or end marker not found.'
        return
    try:
        title = re.search(search_string, contents).group(1)
    except AttributeError:
        wikipedia.output(u"No title found - skipping a page.")
        return
    else:
        page = wikipedia.Page(mysite, title)
        wikipedia.output(page.title())
        if notitle:
          #Remove title (to allow creation of redirects)
          contents = re.sub(search_string, "", contents)
        #Remove trailing newlines (cause troubles when creating redirects)
        contents = re.sub('^[\r\n]*','',contents)
        if page.exists():
            old_text = page.get()
            if not re.search(r'==\s*{{=en=}}\s*==', old_text):
                contents = old_text + '\n'  + contents + '\n'
                commenttext_add = commenttext + ""
                wikipedia.output(u"Page %s already exists, adding to entry!"%title)
                page.put(contents, comment = commenttext_add, minorEdit = False)
            else:
                wikipedia.output(u"Page %s already exists with the section, not adding!"%title)
        else:
            page.put(contents, comment = commenttext, minorEdit = True) # was False (see above)
    findpage(t[location.end()+1:])
    return
 
def main():
    text = []
    f = codecs.open(filename,'r', encoding = config.textfile_encoding)
    text = f.read()
    findpage(text)
 
mysite = wikipedia.getSite()
commenttext = wikipedia.translate(mysite,msg)
for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg, 'pagefromfile')
    if arg:
        if arg.startswith("-start:"):
            starttext=arg[7:]
        elif arg.startswith("-end:"):
            endtext=arg[5:]
        elif arg.startswith("-file:"):
            filename=arg[6:]
        elif arg=="-include":
            include = True
        #elif arg=="-exclude":
            #exclude = True
        elif arg=="-appendtop":
            append = "Top"
        elif arg=="-appendbottom":
            append = "Bottom"
        elif arg=="-force":
            force=True
        elif arg=="-safe":
            force=False
            append="False"
        elif arg=='-notitle':
            notitle=True
        elif arg.startswith("-titlestart:"):
            titlestart=arg[12:]
        elif arg.startswith("-titleend:"):
            titleend=arg[10:]
        elif arg.startswith("-summary:"):
            commenttext=arg[9:]
        else:
            wikipedia.output(u"Disregarding unknown argument %s."%arg)
 
try:
    main()
except:
    wikipedia.stopme()
    raise
else:
    wikipedia.stopme()
'''