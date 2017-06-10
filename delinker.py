# Helper script for delinker and image_replacer

__version__ = '$Id: 955e0f6e63a9189329b4dd96fe21b63cdb2cd879 $'

import wikipedia, config

import sys, os
sys.path.insert(0, 'commonsdelinker')

module = 'delinker'
if len(sys.argv) > 1:
    if sys.argv[1] == 'replacer':
        del sys.argv[1]
        module = 'image_replacer'

bot = __import__(module)
bot.main()
