#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Declaring all global values
mydir = "./"
pwbdir = mydir + "pywikipedia/"
language = "fr"
family = "wiktionary"
mynick = "JackBot"
article = "import"    # Page name, eventually = input()
myuserpage = "Utilisateur:" + mynick
mypage = myuserpage + "/" + article

# Importing modules
import sys
sys.path.append(pwbdir)
from wikipedia import *

# Modifying the wiki
site = getSite(language,family)
page = Page(site,mypage)
pageTemp = page.get()
#pageTemp = "{|test1 test2	test3 test4 \n test5 test6 test7 test8 \n test9|}"
pageEnd = ""
col = 4                 # Number of columns, eventually = input()
cc = 1                  # Current column
endPos = 0

while endPos + 1 < len(pageTemp):
   if cc < col:
      if pageTemp.find("	") < pageTemp.find(" "):
         if pageTemp.find("	") < 1:       # Tab
            if pageTemp.find(" ") > 1:    # Space
               endPos = pageTemp.find(" ")
         else:
            endPos = pageTemp.find("	")
      else:
         if pageTemp.find(" ") < 1:       # Space
            endPos += 1
         else:
            endPos = pageTemp.find(" ")
      if cc == 1:
         pageEnd = pageEnd + pageTemp[0:endPos] + " || [["
         pageTemp = pageTemp[endPos+1:len(pageTemp)]
         cc += 1
      elif cc == 2:
         pageEnd = pageEnd + pageTemp[0:endPos] + "]] || "
         pageTemp = pageTemp[endPos+1:len(pageTemp)]
         cc += 1
      elif cc == 3:
         pageEnd = pageEnd + pageTemp[0:endPos] + " || [["
         pageTemp = pageTemp[endPos+1:len(pageTemp)]
         cc += 1   
   else:
      endPos = pageTemp.find("\n")
      pageEnd = pageEnd + pageTemp[0:endPos] + "]]\n|-\n| "
      pageTemp = pageTemp[endPos+1:len(pageTemp)]
      cc = 1
#print(pageEnd)
page.put(pageEnd)