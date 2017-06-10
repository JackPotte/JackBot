#!/usr/bin/env python
# -*- coding: utf-8  -*-
#$ -m as
#$ -j y
#$ -b y
# SGE integration/interaction: https://wiki.toolserver.org/view/Job_scheduling
# Tip from Merlissimo: use (a=reschedule or abort, s= suspended) to send mail
# by SGE and exitcode 99 to restart the job and 100 to stop it in error state.
"""Wrapper script to use trunk in 'server' mode as cronjob - run scripts using
python pwb.py <name_of_script> <options>

and it will start logging, care about error reporting by mail and SGE.
It will also catch all output to stdout and stderr and report those incidents.
(compare to rewrite/pwb.py)
"""
## @package pwb
#  @brief   General DrTrigonBot Robot(s) Wrapper (see rewrite/pwb.py too)
#
#  @copyright Dr. Trigon, 2008-2013
#
#  @todo      look also at and learn from daemonize.py (@ref daemonize)
#
#  @section FRAMEWORK
#
#  Python wikipedia robot framework, DrTrigonBot.
#  @see http://pywikipediabot.sourceforge.net/
#  @see http://de.wikipedia.org/wiki/Benutzer:DrTrigonBot
#
#  @section LICENSE
#
#  Distributed under the terms of the MIT license.
#  @see http://de.wikipedia.org/wiki/MIT-Lizenz
#
#  @section Usage
#  @li Run any bot on server (according to rewrite/pwb.py):
#  @verbatim python pwb.py <name_of_script> <options> @endverbatim
#
__version__ = '$Id: f3e538a5190167b579d66d8329d387757933a109 $'
#


import sys, os, traceback, shelve

# wikipedia-bot imports
import userlib
# Splitting the bot into library parts
import wikipedia as pywikibot
from pywikibot import version   # JIRA: DRTRIGON-131


## Server Error Handling; send mail to user in case of error
#
#  @todo consider solving/doing this with a logging handler like SMTPHandler
#
def send_mailnotification(text, subject):
    username = pywikibot.config.usernames[pywikibot.config.family][pywikibot.config.mylang]
    pos = username.lower().find('bot')
    username = username[:pos] if (pos > 0) else username

    pywikibot.output(u'Sending mail "%s" to "%s" as notification!' % (subject, username))
    # JIRA: DRTRIGON-87; output even more debug info (tip by: valhallasw@arctus.nl)
    site = pywikibot.getSite()
    pywikibot.output(u'Bot allowed to send email: %r' % (site.isAllowed('sendemail'),))
    pywikibot.output(u'Permissions: %r' % (site._rights,))
    if not site.isAllowed('sendemail'):
        pywikibot.output(u'Try getting new token: %r' % (site.getToken(getagain=True),))
    usr = userlib.User(site, username)
    try:
        if usr.sendMail(subject=subject, text=text):    # 'text' should be unicode!
            return
    except:  # break exception handling recursion
        pywikibot.exception(tb=True)
        pywikibot.error(u'mail to %s could not be sent!' % username)

    pywikibot.output(u'May be not logged in - try to send emergency email')
    try:
        import smtplib
        from email.mime.text import MIMEText
        # sender's and recipient's email addresses
        FROM = "%s@toolserver.org" % username.lower()
        TO   = [FROM]   # must be a list
        # Create a text/plain message
        msg = MIMEText(text)
        msg['Subject'] = "!EMERGENCY! " + subject
        msg['From']    = FROM
        msg['To']      = ", ".join(TO)
        # Send the mail
        server = smtplib.SMTP("localhost")
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()
    except:  # break exception handling recursion
        pywikibot.exception(tb=True)
        pywikibot.error(u'emergency mail to %s could not be sent!' % TO)


## Bot Output Redirecting And Logging; to assure all output is logged
#
#  @todo consider using 'rrdtool' to improve logging (and logging_statistics as
#        well as creating graphs in panel.py - may be with 'bottle' as webserver)
#  @see  http://segfault.in/2010/03/python-rrdtool-tutorial/
#
class BotLoggerObject:
    def __init__(self, layer='stdout'):
        self._layer = layer
    def write(self, string):
        for line in string.strip().splitlines():
            pywikibot.critical('[%s] %s' % (self._layer, line))
    def close(self):
        pass
    def flush(self):
        pass


# SGE: exit errorlevel
ERROR_SGE_ok      = 0    # successful termination, nothing more to do
ERROR_SGE_stop    = 1    # error, but not for SGE
ERROR_SGE_restart = 99   # restart the job
ERROR_SGE_lock    = 100  # stop in error state (prevents re-starts)

exitcode = ERROR_SGE_stop       # action in error case (stop with error)
#exitcode = ERROR_SGE_restart    # -------- " --------- (restart)
#exitcode = ERROR_SGE_lock       # -------- " --------- (stop and lock)


if len(sys.argv) < 2:
    raise RuntimeError("Not enough arguments defined.")
else:
    logname = pywikibot.config.datafilepath('logs', '%s.log')
    logfile = logname % ''.join([os.path.basename(sys.argv[0])]+sys.argv[1:])

    arg = pywikibot.handleArgs()                            # '-family' and '-lang' have to be known for log-header
    sys.stdout = BotLoggerObject(layer='stdout')            # handle stdout
    sys.stderr = BotLoggerObject(layer='stderr')            # handle stderr
    if not pywikibot.simulate:                              # suppress console output
        pywikibot.ui.stdout = open(os.devnull, 'w')         #
        pywikibot.ui.stderr = open(os.devnull, 'w')         #
        #pywikibot._outputOld = lambda text, **kwargs: None #
    # may be use "log = ['*']" in 'user-config.py' instead
    pywikibot.setLogfileStatus(True, logfile, header=True)  # set '-log' to catch all
    # check: http://de.wikipedia.org/wiki/Hilfe:MediaWiki/Versionen

    path = os.path.split(sys.argv[0])[0]
    cmd  = sys.argv.pop(1)
    cmd  = cmd.lstrip(u'-')
    if u'.py' not in cmd.lower():
        cmd += u'.py'
    sys.argv[0] = os.path.join(path, cmd)
    bot_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    error = u''
    try:
        __release = version.getversiondict()
        d = shelve.open(pywikibot.config.datafilepath('cache', 'state_bots'))
        d['bot_control'] = {'release_rev': str(__release['rev']),
                            'release_ver': __release['hsh'][:7],
                             'online_ver': version.getversion_onlinerepo()[:7],
                           }
        pywikibot.output(d['bot_control'])
        pywikibot.output(u'=== ' * 14)
        d.close()

        sys.path.append(os.path.split(sys.argv[0])[0])
        execfile(sys.argv[0])

        exitcode = ERROR_SGE_ok
        pywikibot.output(u'')
        pywikibot.output(u'DONE')
    except:
        pywikibot.exception(tb=True)
        error = traceback.format_exc()
        if pywikibot.logger.isEnabledFor(pywikibot.DEBUG):
            exitcode = ERROR_SGE_ok    # print traceback of re-raised errors by skipping sys.exit()
            raise
        else:
            send_mailnotification(error, u'Bot ERROR')
        pywikibot.output(u'')
        pywikibot.warning(u'DONE with Exception(s) occured in Bot')
    finally:
        site = pywikibot.getSite()
        name = str('%s-%s-%s' % (bot_name, site.family.name, site.lang))
        d = shelve.open(pywikibot.config.datafilepath('cache', 'state_bots'))
        d[name] = {'error':     str(bool(error)),
                   'traceback': str(error.encode('utf-8')),
                   'timestamp': str(pywikibot.Timestamp.now().isoformat(' ')),
                  }
        d.close()

        pywikibot.stopme()
        (sys.stdout, sys.stderr) = (sys.__stdout__, sys.__stderr__)

        # use exitcode to control SGE (restart or stop with sending mail)
        # re-raised errors occouring in 'except' clause are skipped because
        # of raised 'SystemExit' exception by sys.exit()
        sys.exit(exitcode)
