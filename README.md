JackBot
=======

This wiki bot has performed thousands of modifications on several wikis: https://meta.wikimedia.org/wiki/User:JackBot

![Logo](https://upload.wikimedia.org/wikipedia/commons/f/f2/Pywikibot-logo-suggestion-mediawiki.svg)


# Installation

```
git clone https://github.com/JackPotte/JackBot.git
cd JackBot
devops/update_Pywikibot.sh
```

## Speed optimization
To accelerate the treatments:
* vim user-config.py: maxthrottle & put_throttle = 0
* vim core/pywikibot/throttle.py, time.sleep(0).

# Usage

See [JackBot.sh](JackBot.sh)

# Pull requests

If you don't use https://www.python.org/dev/peps/pep-0008/, 
please at least avoid any line larger than 150 characters, to allow a quick review.

The strategy of this bot is to parse without any tree, so it can treat pages in error but should be careful about nested templates and tags.
