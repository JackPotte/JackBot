JackBot
=======

This wiki bot has performed thousands of modifications on several wikis: https://meta.wikimedia.org/wiki/User:JackBot

**Pull requesters:** if you don't use https://www.python.org/dev/peps/pep-0008/, 
please at least avoid any line larger than 150 characters, to allow a quick review.

![Logo](https://upload.wikimedia.org/wikipedia/commons/f/f2/Pywikibot-logo-suggestion-mediawiki.svg)


# Installation

* Download Pywikibot on http://tools.wmflabs.org/pywikibot/ and put it in JackBot/core.
* Follow https://www.mediawiki.org/wiki/Manual:Pywikibot/i18n/fr to achieve the installation.
* pip install regex
* pip install requests
* To accelerate the treatments:
    * modify throttle.py:254 with time.sleep(0).
    * and user-config.py:186
