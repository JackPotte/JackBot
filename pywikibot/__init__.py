# wikipedia.py will monkey-patch this module to look completely
# alike wikipedia itself...

try:
    import wikipedia
except Exception, e:
    print e
    print u'Serious import error; pywikibot not available - was it configured?'
