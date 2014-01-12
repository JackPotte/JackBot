import userlib
import wikipedia as pywikibot
for arg in pywikibot.handleArgs():
	if arg.startswith('-user'):
		user = arg[len('-user:'):]
	elif arg.startswith('-summary'):
		summary = arg[len('-summary:'):]
	elif arg.startswith('-length'):
		expiry = arg[len('-length'):]
block.user(self, expiry=expiry, reason=summary, anon=True, noCreate=False,
          onAutoblock=False, banMail=False, watchUser=False, allowUsertalk=True,
          reBlock=False, hidename=False)
