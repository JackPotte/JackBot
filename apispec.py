# -*- coding: utf-8  -*-
"""
This is a library for querying special pages through API.
A supported feature does not mean it is complete.
Feel free to continue. :-) It shall be large and comprehensive someday.
No version checks or API existence checks implemented.
Different features require different MW versions as shown in local docstrings.
Tested on Wikipedia. Other MediaWiki installations may provide different APIs,
please check documentation at /w/api.php if something does not work.
You may find detailed help for each feature in the code.

Supported features:
    Blocks      Querying valid local blocks, based on Special:BlockList.
"""
"""
General help to continue: http://www.mediawiki.org/wiki/API:Lists
http://en.wikipedia.org/wiki/Special:ApiSandbox is good for experiments.

TODO:
* Handling errors and warnings where necessary. For example: disabled modules
    (may be useful for non-WM wikis)
    http://www.mediawiki.org/wiki/API:Errors_and_warnings#Disabled_modules
"""
#
# (C) Bináris, 2012
# (C) Pywikipedia bot team, 2012
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'

import datetime, re
import wikipedia as pywikibot
import query

site = pywikibot.getSite()

#Some functions for datetime conversion
def iso(t):
    """Removes fraction part of Python-generated time and adds a Z for UTC"""
    s = t.isoformat()
    return s[:s.find('.')] + 'Z'

def uniso(timestamp):
    """Removes T and Z from an ISO 8601-formatted text for readability."""
    return timestamp.replace('T', ' ').replace('Z', '')

def dt(timestamp):
    """Converts a MediaWiki timestamp to a Python-compatible datetime object"""
    #Timestamps come as "2012-01-30T16:47:57Z"
    #Be sure to exclude "infity" before calling this!
    l = timestamp.split('T')
    try:
        d = l[0].split('-') #The date
        t = l[1][:-1].split(':') #The time
        d = [int(x) for x in d]
        t = [int(x) for x in t]
        return datetime.datetime(d[0], d[1], d[2], t[0], t[1], t[2])
    except IndexError:
        print 'Erroneous timestamp:', timestamp
        return datetime.datetime(1,1,1,1,1,1) #This may be handled as error

def duration(x):
    """
    Duration of a finite block or protection.
    Don't call for infinite ones. Or at least don't blame me.
    """
    return (dt(x['expiry']) - dt(x['timestamp'])).days

#API may change. This is a general dictionary with all possible keys that
#may be returned in case of KeyError. If you get this as result, please
#report a bug with all possible circumstances.
errordic = {
    'id': -1,
    'userid': -1,
    'byid': -1,
    'user': 'This is an error message, has API format changed?',
    'by': 'This is an error message, has API format changed?',
    'reason': 'This is an error message, has API format changed?',
    'rangestart': 'This is an error message, has API format changed?',
    'rangeend': 'This is an error message, has API format changed?',
    'timestamp': '0000-00-00T00:00:00Z',
    'expiry': '0000-00-00T00:00:00Z',
}

class Blocks(object):
    """
    A class for querying valid local blocks. Based on Special:BlockList.
    That means it won't handle expired or solved blocks, nor globals.
    (Although newly expired blocks may appear in the list for a time, and
    autoblocks may appear on the day of expiry after expiration.)
    Requires MW 1.12.
    All the methods return a list of dictionaries, unless otherwise stated.
    Each dictionary represents a block. Keys are shown at
      http://www.mediawiki.org/wiki/API:Blocks
    under 'bkprop'. Note that 'user' key is not present if it is an autoblock,
    and flags are not present if they are not valid for that block. It is your
    task to handle this. Even numeric values such as id's come as strings!
    The list is ordered by timestamp of applying the block unless noted.
    Timestamps of beginning and expiry are in UTC and ISO 8601 format.
        http://www.mediawiki.org/wiki/API:Data_formats#Timestamps
    Convert them to local time if necessary.
    See http://docs.python.org/library/datetime.html for help.

    Methods:
    1. General lists:
    allblocks       List of all effective blocks
    autoblocks      List of effective autoblocks
    notautoblocks   Direct (not automatic) blocks. Required by other methods.
    anonblocks      List of IP blocks, including range blocks
    anonblocks_norange  List of IP blocks, excluding range blocks
    rangeblocks     List of range blocks
    reguserblocks   List of blocks concerning registered users, not anons
    byadmin         Blocks raised by a given admin
    user	        Blocks of the given user or single IP (exact match)
                        (Only direct blocks for the given IP, not range blocks)
    userfragment	Blocks of the given user or single IP
                        You may give any part of the username.
    userregex	    Blocks of the given user or single IP
                        Give a regex with r'...' or ur'...'
    IP	            Blocks of the given single IP or range (max. /16)
                        If you give an IP, this will return also range blocks
                        concerning this IP (not like user()).
    reason	        Blocks raised with the given reason (exact match)
    reasonfragment	Blocks raised with the given reason
                        You may give any part of the reason, e.g. 'andalism'
    reasonregex	    Blocks raised with the given reason (regex)
    Remarks:    user-like and reason-like methods are case sensitive.
                Use user() and IP() whenever appropriate. They are much faster
                and cause less server load!
                "Fragment" and "regex" methods are for hunting vandals with
                some peculiar pattern or examining blocking habits of admins.
                Regexes will be searched for rather than matched. This means
                you have to begin them with ^ if you want to find them at the
                beginning of the string.

    2. Simplified lists of blocked users/IPs:
    These lists, unlike others, contain simple Unicode strings rather than
    block directories. The first one is ordered chronologically by date of
    blocking, which is useful for hunting the reincarnations of a vandal,
    while the others in alphanumerical order.
    blockedusernames_chrono     List of blocked users in chronolocical order
    blockedusernames            List of blocked users in alphabetical order
    blockedanons                All blocked IPs (including range blocks)
    blockedanons_norange        Standalone blocked IPs (excluding range blocks)
    blockedranges               List of blocked ranges

    3. By expiry:
    finiteblocks    List of all finite blocks
    infiniteblocks  List of all infinite and indefinite blocks
    expindays       Blocks expiring within n days (from the second of calling)
    expnotindays    Finite blocks not expiring within n days
                    (use with infiniteblocks to get all the remaining blocks)
    expuntil        Blocks expiring by the given timestamp
    expafter        Finite blocks expiring after the given timestamp
                    (use with infiniteblocks to get all the remaining blocks)
                    For valid timestamps see
                    http://www.mediawiki.org/wiki/API:Data_formats#Timestamps

    The next three are ordered by ascending duration:
    shorterthan     List of blocks shorter than given number of days
    longerthan      List of blocks at least as long as given number of days
                    (use with infiniteblocks to get all the remaining blocks)
    between         List of blocks whose duration is in the given interval

    4. Auxiliary:
    display(block)  A simple function for lazy programmers that will display
                    human-readable details of the given dictionary that
                    represents a block (with English keywords at this time).
                    You may use it with pywikibot.output or insert into
                    a wikipage between <pre> tags. This may be iterated or
                    joined on a list of blocks, but don't blame me if your
                    monitor is not tall enough.
                    Should 'bot' be an instance of this class and b a block,
                    bot.display(b) returns the text in Unicode.
                    It displays existing flags of the block. Missing flags are
                    not set for this block. For meaning of flags see
                    http://www.mediawiki.org/wiki/API:Blocks
                    Possible flags: 'automatic', 'anononly', 'nocreate',
                    'autoblock', 'noemail', 'allowusertalk', 'hidden'.
    displaylist     Takes a list of blocks as argument and creates a long human
                    readable text of it. Use as above.
                    E.g. pywikibot.output(bot.displaylist(bot.expindays(1)))
                    displays blocks expiring within 24 hours.

    Optional parameters:
    site        site as usual, autodetected if missing
                This has some bug at the moment, but works well in home wiki.
    top         'new'/'old' (newest or oldest block on top; default='new')
    limit       Maximum number of blocks to get in one query as integer or
                string. Defaults to 5000. That is the allowed maximum for bots
                in Wikimedia wikis. You MUST set it to no more than 500 if your
                bot does not have a flag.
                See http://www.mediawiki.org/wiki/API:Query_-_Lists#Limits
                Bot will repeat queries until it is necessary, so you get the
                whole list anyway.
                !! Setting this value too low may result in an infinite loop
                or duplicated results. Use as great limit as possible.
                See https://bugzilla.wikimedia.org/show_bug.cgi?id=34029
                Additionally, decreasing this limit will cause a
                quasi-exponential increase of running time!

    help: http://www.mediawiki.org/wiki/API:Blocks
    TODO:
    * Explore the bug of site parameter
    * A function listing all blocked IPs, expanding ranges
    * Some statistics from blocks
    """

    #################################################
    #          Methods for internal use             #
    #################################################
    def __init__(self, site=site, top='new', limit=5000):
        self.site = site
        self.bkdir = ['older', 'newer'][top=='old'] #a bit strange
        # bkdir: Direction to list in.
        #older: List newest blocks first (default).
        #Note: bkstart has to be later than bkend.
        #newer: List oldest blocks first. Note: bkstart has to be before bkend.
        self.bklimit = limit #Allowed maximum for bots=5000
        self.empty()

    def empty(self):
        """
        Sets the parameters needed by all methods, and clears the others.
        """
        self.params = {
            'action':   'query',
            'list':     'blocks',
            'bklimit':  self.bklimit,
            'bkdir':    self.bkdir,
            'bkprop':
                'id|user|userid|by|byid|timestamp|expiry|reason|range|flags',
        }

    def query(self):
        result = query.GetData(self.params, site=self.site)
        blocklist = result['query']['blocks']
        #Todo: handle possible errors (they will cause KeyError at this time)
        while 'query-continue' in result:
            self.params.update(result['query-continue']['blocks'])
            result = query.GetData(self.params)
            blocklist += result['query']['blocks']
        #Finally we remove possible duplicates. This piece of code may be
        #removed after successful closing of
        #https://bugzilla.wikimedia.org/show_bug.cgi?id=34029
        for b in blocklist:
            if blocklist.count(b) > 1:
                blocklist.pop(blocklist.index(b))
        return blocklist

    def IPsortkey(self, IP):
        """
        Sortkey for IPs given as strings. Assumes a properly formatted
        IP string, either standalone or range.
        """
        l1 = IP.split('/')
        l2 = l1[0].split('.') #IP part without range
        newlist = [('0' + s)[-3:] for s in l2]
        s = '.'.join(newlist)
        if len(l1) > 1:
            s += '/' + l1[1]
        return s

    #################################################
    #                General lists                  #
    #################################################
    def allblocks(self):
        """Returns complete list"""
        self.empty()
        return self.query()

    def autoblocks(self):
        """Returns autoblocks"""
        self.empty()
        self.params['bkend'] = \
            iso(datetime.datetime.utcnow() - datetime.timedelta(1))
        return filter(lambda x: 'user' not in x, self.query())
        #Autoblocks back to previous day 00:00:00 UTC appear in the list even
        #if they are no more in effect, but we don't query them.

    def notautoblocks(self):
        """Returns direct (not automatic) blocks. Required by other methods."""
        self.empty()
        return filter(lambda x: 'user' in x, self.query())

    def anonblocks(self):
        """Returns anonblocks, including range blocks"""
        self.empty()
        return filter(lambda x: x['userid'] == '0', self.notautoblocks())

    def anonblocks_norange(self):
        """Returns anonblocks, excluding range blocks"""
        self.empty()
        try:
            return filter(lambda x: x['rangestart'] == x['rangeend'],
                            self.anonblocks())
        except KeyError:
            return [errordic]

    def rangeblocks(self):
        """Returns range blocks"""
        self.empty()
        try:
            return filter(lambda x: x['rangestart'] != x['rangeend'],
                            self.anonblocks())
        except KeyError:
            return [errordic]

    def reguserblocks(self):
        """Returns block concerning registered users, not anons"""
        self.empty()
        return filter(lambda x: x['userid'] > '0', self.notautoblocks())

    def byadmin(self, admin):
        """Returns blocks raised by given admin"""
        self.empty()
        return filter(lambda x: x['by']==admin, self.query())

    def user(self, user):
        """Returns blocks of the given user or single IP"""
        self.empty()
        self.params['bkusers'] = user
        return self.query()

    def userfragment(self, user):
        """Returns blocks of the given user or single IP (part of name)"""
        self.empty()
        return filter(lambda x: user in x['user'], self.notautoblocks())

    def userregex(self, regex):
        """Returns blocks of the given user or single IP (regex)"""
        self.empty()
        return filter(
                lambda x: re.search(regex, x['user']), self.notautoblocks())

    def IP(self, IP):
        """Returns blocks of the given single IP or range (max. /16)"""
        self.empty()
        self.params['bkip'] = IP
        return self.query()

    def reason(self, reason):
        """Returns blocks raised with the given reason (exact text)"""
        self.empty()
        return filter(lambda x: x['reason'] == reason, self.query())

    def reasonfragment(self, reason):
        """Returns blocks raised with the given reason (part of it)"""
        self.empty()
        return filter(lambda x: reason in x['reason'], self.query())

    def reasonregex(self, regex):
        """Returns blocks raised with the given reason (regex)"""
        self.empty()
        return filter(
                lambda x: re.search(regex, x['reason']), self.allblocks())

    #################################################
    #        Lists of blocked users/IPs             #
    #################################################
    #These methods return ordered list of Unicode strings
    def blockedusernames_chrono(self):
        return [b['user'] for b in self.reguserblocks()]

    def blockedusernames(self):
        return sorted(self.blockedusernames_chrono())

    def blockedanons(self):
        return sorted(
            [b['user'] for b in self.anonblocks()], key=self.IPsortkey)

    def blockedanons_norange(self):
        return sorted(
            [b['user'] for b in self.anonblocks_norange()], key=self.IPsortkey)

    def blockedranges(self):
        return sorted(
            [b['user'] for b in self.rangeblocks()], key=self.IPsortkey)

    #################################################
    #             Lists by expiry                   #
    #################################################
    def finiteblocks(self):
        """Returns finite blocks"""
        self.empty()
        return filter(lambda x: x['expiry'][0].isdigit(), self.query())

    def infiniteblocks(self):
        """Returns infinite and indefinite blocks"""
        self.empty()
        return filter(lambda x: x['expiry'].isalpha(), self.query())

    def expindays(self, days):
        """Returns blocks expiring within days days"""
        limit = iso(datetime.datetime.utcnow() + datetime.timedelta(days))
        return filter(lambda x: x['expiry'] <= limit, self.finiteblocks())

    def expnotindays(self, days):
        """Returns finite blocks NOT expiring within days days"""
        limit = iso(datetime.datetime.utcnow() + datetime.timedelta(days))
        return filter(lambda x: x['expiry'] > limit, self.finiteblocks())

    def expuntil(self, timestamp):
        """Returns blocks expiring by timestamp"""
        return filter(lambda x: x['expiry'] <= timestamp, self.finiteblocks())

    def expafter(self, timestamp):
        """Returns finite blocks NOT expiring by timestamp"""
        return filter(lambda x: x['expiry'] > timestamp, self.finiteblocks())

    def shorterthan(self, days):
        """Returns finite blocks shorter than day"""
        return sorted(
            filter(lambda x: duration(x) < days, self.finiteblocks()),
            key = duration)

    def longerthan(self, days):
        """Returns finite blocks longer than or equal to day"""
        return sorted(
            filter(lambda x: duration(x) >= days, self.finiteblocks()),
            key = duration)

    def between(self, days1, days2):
        """
        Returns finite blocks whose duration is in closed interval
        [day1,day2]
        """
        return sorted(
          filter(lambda x: days1 <= duration(x) <= days2, self.finiteblocks()),
          key = duration)

    #################################################
    #              Auxiliary methods                #
    #################################################
    def display(self, block):
        """
        Simple displayer for a block dictionary. Use with pywikibot.output
        or e-mail it or insert into a wikipage with <pre>.
        """
        w = 21 #width for justification
        flags = ['automatic', 'anononly', 'nocreate', 'autoblock', 'noemail',
                 'allowusertalk', 'hidden']
        s = 'Data for block #%s' % block['id']
        s += '\nBlocked user:'.ljust(w)
        try:
            s += block['user']
            if 'userid' in block and block['userid'] > '0':
                s += ' (#%s)' % block['userid']
        except KeyError:
            s += 'n/a (autoblock)'
        if 'rangestart' in block and 'rangeend' in block and \
                block['rangestart'] != block['rangeend']:
            s += '\nRange block:'.ljust(w) + u'%s–%s' %  \
                (block['rangestart'],block['rangeend'])
        s += '\nAdmin:'.ljust(w) + '%s (#%s)' % (block['by'], block['byid'])
        s += '\nBeginning in UTC:'.ljust(w) + uniso(block['timestamp'])
        s += ('\nExpiry%s:' \
              % ['', ' in UTC'][block['expiry'][0].isdigit()]).ljust(w)
        s += uniso(block['expiry'])
        s += '\nFlags:'.ljust(w)
        s += ', '.join(filter(lambda x: x in block, flags))
        s += '\nReason:'.ljust(w) + block['reason'] + '\n'
        return s

    def displaylist(self, blocklist):
        """
        Returns a long human readable version of a blocklist, ready for
        pywikibot.output. Usually too long for direct display.
        """
        return '\n'.join([self.display(b) for b in blocklist])

if __name__ == '__main__':
    pywikibot.handleArgs() #for help
    pywikibot.output(
            'This is a library for querying special pages through API.')
    pywikibot.output('Use this module through import or with -help.')
