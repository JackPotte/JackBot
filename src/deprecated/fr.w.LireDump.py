#!/usr/bin/env python
# coding: utf-8
# Ce script filtre les dumps volumineux.

import os
input = u'frwiki-20140331-all-titles.txt'
output = u'frwiki-filtre.txt'
chaine = u'/Modèle Cadre'

DUMP = open(input, 'r')
RESULT = open(output, 'w')
while 1:
	PageDump = DUMP.readline()
	PageDump = PageDump[:PageDump.find("\t")].decode('utf8')
	if PageDump == '': break
	print PageDump.encode('utf8')
	if PageDump.find(chaine) != -1:
		RESULT.write(u'# [[')
		RESULT.write(PageDump.encode('utf8'))
		RESULT.write(u']]\n')
DUMP.close()
RESULT.close()