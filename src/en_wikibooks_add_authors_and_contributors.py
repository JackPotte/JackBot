#!/usr/bin/env python
# coding: utf-8
"""
This script adds authors and contributors in the wikibooks
"""
import pywikibot
import requests
from bs4 import BeautifulSoup
import os
import sys
# JackBot
dir_src = os.path.dirname(__file__)
sys.path.append(dir_src)
sys.path.append(os.path.join(dir_src, 'lib'))
from lib import *

site_language, site_family, site = get_site_by_file_name(__file__)


def update_book(title):
    page = pywikibot.Page(site, f'{title}/Authors & Contributors')
    if '%2F' in title:
        page = pywikibot.Page(site, title.replace('%2F', '') + '/Authors & Contributors')

    book = title.replace(' ', '+')
    print(book)
    url = f'https://meta.toolforge.org/catanalysis/?title={book}&cat=0&wiki=' + site_language + site_family
    print(url)
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    usernames = []
    for link in soup.find_all('a'):
        linkstr = link.get('href')
        if linkstr.startswith(
                'https://en.wikibooks.org/wiki/user:') and linkstr != 'https://en.wikibooks.org/wiki/user:(Anonymous)':
            username = linkstr[35:]
            if not username in usernames and len(username) > 0 and not username in bots:
                usernames.append(username)
    print(usernames)

    try:
        temp = 'This list is updated automatically by [[User:AuthorsAndContributorsBot|AuthorsAndContributorsBot]]. Please do not update it manually.\n\n'
        for user in usernames:
            if not '>' in user:
                temp += '#{{usercheck|' + user + '}}\n'
            else:
                temp += '#' + user + '\n'
        temp += '\n{{' + 'BookCat}}'
        print(title)
        print(temp)

        if page.text != temp:
            page.text = temp
            page.save(
                summary=f'Automatically updating the list of Authors and Contributors based on [{url}]',
                minor=False,
                botflag=True,
            )
    except Exception as exception:
        print(exception)


def get_book_list():
    page = pywikibot.Page(site, 'User:AuthorsAndContributorsBot/List of books')
    text = page.text
    books = text.split('<br>')
    print(books)
    return books


# TODO merge with https://en.wikibooks.org/w/index.php?title=Special:ListUsers&group=bot
def get_bots_list():
    page = pywikibot.Page(site, 'User:AuthorsAndContributorsBot/blacklist')
    text = page.text
    bots = text.split('<br>')
    print(bots)
    return bots


bots = get_bots_list()
for book in get_book_list():
    update_book(book)
