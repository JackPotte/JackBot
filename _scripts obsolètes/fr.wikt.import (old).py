#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Declaring all global values
mydir = "./"
pwbdir = mydir + "pywikipedia/"
language = "fr"
family = "wiktionary"
mynick = "JackBot"
word = "mot"
myuserpage = "Utilisateur:" + mynick
mypage = myuserpage + "/" + word
 
# Importing modules
import sys
sys.path.append(pwbdir)
from wikipedia import *
import urllib
 
# DAF8
data = urllib.urlopen("http://www.cnrtl.fr/definition/academie8/" + word,"utf-8").read()
beginTag = """lexicontent"""
endTag="""<div id="footer">"""
startPos = data.find(beginTag)
page2 = ""
while startPos > -1:
    endPos = data.find(endTag,startPos+1)
    if endTag == -1:
      break
    else:
      page2 = "",data[startPos+len(beginTag):endPos]
      startPos = data.find(beginTag,endPos+1)
 
# Littré
data = urllib.urlopen("http://francois.gannaz.free.fr/Littre/xmlittre.php?requete=" + word + "&submit=Rechercher", "utf-8").read()
beginTag = """variante">"""
endTag="""<!--fin du corps-->"""
startPos = data.find(beginTag)
page3 = ""
while startPos > -1:
    endPos = data.find(endTag,startPos+1)
    if endTag == -1:
      break
    else:
      page3 = "",data[startPos+len(beginTag):endPos]
      startPos = data.find(beginTag,endPos+1)
 
# Formatage
if page2 == "" and page3 == "":
  page1 = ""
else:
  page1 = u"<br>{{ébauche}}<br>"
page2 = unicode(page2)
page3 = unicode(page3)
page4 = u"<br>{{-réf-}}<!--Bot check DAF8 + Littré-->"
 
# Modifying the wiki
site = getSite(language,family)
page = Page(site,mypage)
page5 = page.get() +  page1 + page4 + unicode(page2) + unicode(page3)
#print page5
page.put(page5)
