#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Externals modules automatic setup checker and installer for various OS.
"""

#
# (C) DrTrigon, 2013
# (C) Pywikipedia team, 2013
#
# Distributed under the terms of the MIT license.
#
# Strongly inspired by files beeing part of VisTrails distribution
#   utils/installbundle.py
#   utils/requirements.py
# Copyright (C) 2006-2010 University of Utah. All rights reserved.
# GNU General Public License version 2.0 by the Free Software Foundation
#
__version__ = '$Id$'
#


# supports: 0. svn:externals / git submodule
#           1. package management system (yum, apt-get, ...)
#           2. download from url (or svn, git repo)
#           3. checkout from mercurial repo ('hg clone ...' since url not
#              available)
#           (what about python eggs?!)
# dependencies: (svn, python)
#               yum, apt-get or whatever your system uses
#               mercurial (hg)
#               patch (unix/linux & gnuwin32 version/flavour)
modules_needed = {
          'patch.exe': ({}, # for win32 only, unix/linux is already equipped with a patch tool
                        {  'url': 'http://downloads.sourceforge.net/project/gnuwin32/patch/2.5.9-7/patch-2.5.9-7-bin.zip',
                          'path': 'bin/patch.exe'},
                        {}),                                               # OK
            'crontab': ({},
                        #{  'url': 'https://github.com/josiahcarlson/parse-crontab/archive/master.zip',
                        #  'path': 'parse-crontab-master/crontab',}),       # OK
                        {  'url': 'https://github.com/josiahcarlson/parse-crontab/archive/1ec538ff67df6a207993a6c5b6988f4f628c5776.zip',
                          'path': 'parse-crontab-1ec538ff67df6a207993a6c5b6988f4f628c5776/crontab',},
                        {}),                                               # OK
                'odf': ({},
                        #{  'url': 'https://pypi.python.org/packages/source/o/odfpy/odfpy-0.9.6.tar.gz',
                        #  'path': 'odfpy-0.9.6/odf',}),                    # OK
                        {  'url': 'https://pypi.python.org/packages/source/o/odfpy/odfpy-0.9.4.tar.gz',
                          'path': 'odfpy-0.9.4/odf'},
                        {}),                                               # OK
           'openpyxl': ({},
                        {  'url': 'https://bitbucket.org/ericgazoni/openpyxl/get/1.5.6.tar.gz',
                          'path': 'ericgazoni-openpyxl-e5934500ffac/openpyxl'},
                        {}),                                               # OK
#           'spelling': $ svn propedit svn:externals externals/.
#                         spelling http://svn.wikimedia.org/svnroot/pywikipedia/trunk/spelling/
#                       $ git submodule add https://gerrit.wikimedia.org/r/p/pywikibot/spelling.git externals/spelling
   'BeautifulSoup.py': ({'linux-fedora': ['python-BeautifulSoup'],
                         'linux-ubuntu': ['python-beautifulsoup']},
                        {  'url': 'https://pypi.python.org/packages/source/B/BeautifulSoup/BeautifulSoup-3.2.0.tar.gz',
                          'path': 'BeautifulSoup-3.2.0/BeautifulSoup.py'},
                        {}),                                               # OK
             'irclib': ({'linux-fedora': ['python-irclib'],
                         'linux-ubuntu': ['python-irclib']},
                        {}, # http://python-irclib.sourceforge.net/
                        {}),                                               # OK
   'mwparserfromhell': ({},
                        {  'url': 'https://github.com/earwig/mwparserfromhell/archive/v0.2.zip',
                        #{  'url': 'https://github.com/earwig/mwparserfromhell/archive/master.zip',
                          'path': 'mwparserfromhell-0.2/mwparserfromhell'},
                        {}),                                               # OK
          'colormath': ({'linux-fedora': [],
                         'linux-ubuntu': ['python-colormath'],},
                        {  'url': 'https://github.com/gtaylor/python-colormath/archive/master.zip',
                          'path': 'python-colormath-master/colormath',},
                        {}),                                               # OK
               'jseg': ({},
                        {  'url': 'http://vision.ece.ucsb.edu/segmentation/jseg/software/jseg.zip',
                          'path': 'jseg',
                         #$ diff -Nau --exclude="*.o" --exclude="*.pyc" --exclude="segdist_cpp*" TEST_jseg/ jseg/ > patch-jseg
                         'patch': 'patch-jseg'},
                        {}),                                               # OK
       'jseg/jpeg-6b': ({},
                        {  'url': 'http://vision.ece.ucsb.edu/segmentation/jseg/software/jpeg-6b.zip',
                          'path': 'jpeg-6b',},
                        {}),                                               # OK
              '_mlpy': ({},
                        {  'url': 'http://downloads.sourceforge.net/project/mlpy/mlpy%203.5.0/mlpy-3.5.0.tar.gz',
                          'path': 'mlpy-3.5.0/mlpy'},
                        {}),                                               # OK
           '_music21': ({},
                        {  'url': 'http://music21.googlecode.com/files/music21-1.4.0.tar.gz',
                          'path': 'music21-1.4.0',
                         #$ diff -Naur --exclude="*.pyc" TEST__music21/ _music21/ > patch-music21
                         'patch': 'patch-music21'},
                        {}),                                               # OK
# TODO: vvv (future; enable for and use in 'catimages.py', patch needed)
           '_ocropus': ({},
                        {},
                        {  'url': 'https://code.google.com/p/ocropus',
                           'rev': 'ocropus-0.6'}),                         # OK
# TODO: vvv (further clean-up and unlink - check with 'svn list')
#             'opencv': $ svn propedit svn:externals externals/.
#                         opencv https://svn.toolserver.org/svnroot/drtrigon/externals/opencv
#                       $ svn propedit svn:externals externals/opencv/haarcascades/haartraining/
#                         HaarTraining https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/HaarTraining
#                         HaarTraining.tar.gz https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/HaarTraining.tar.gz
#                         convert_cascade.c https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/convert_cascade.c
#                         create_pos_neg.py https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/create_pos_neg.py
#                         createtestsamples.pl https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/createtestsamples.pl
#                         createtrainsamples.pl https://svn.toolserver.org/svnroot/drtrigon/externals/haartraining/createtrainsamples.pl
'opencv/haarcascades': ({},
                        {  'url': 'https://svn.toolserver.org/svnroot/drtrigon/externals/haarcascades-full.tar.gz',
                          'path': 'haarcascades'},
                        {}),                                               # OK
#          'pdfminer' is not used anymore/at the moment...
#       'pycolorname': $ svn propset svn:externals 'pycolorname https://svn.toolserver.org/svnroot/drtrigon/externals/pycolorname' externals/.
             'pydmtx': ({'linux-fedora': ['python-libdmtx'],
                         'linux-ubuntu': ['libdmtx-dev']},
                        {  'url': 'https://github.com/dmtx/dmtx-wrappers/archive/master.zip',
                          'path': 'dmtx-wrappers-master/python',
                         #$ diff -Nau --exclude="*.pyc" TEST_pydmtx/ pydmtx/ > patch-pydmtx
                         'patch': 'patch-pydmtx'},
                        {}),                                               # OK
             'py_w3c': ({},
                        {  'url': 'https://bitbucket.org/nmb10/py_w3c/downloads/py_w3c-v0.1.0.tar.gz',
                          'path': 'py_w3c-0.1.0/py_w3c'},
                        {}),                                               # OK
# TODO: vvv (include)
#               'TEST_slic': ({},
#                        {  'url': 'http://ivrg.epfl.ch/files/content/sites/ivrg/files/supplementary_material/RK_SLICsuperpixels/SLICSuperpixelsAndSupervoxelsCode.zip',
#                          'path': 'SLICSuperpixelsAndSupervoxelsCode/SLICSuperpixels',}),# OPEN
#               'TEST_slic': ({},
#                        {  'url': 'https://github.com/amueller/slic-python/archive/master.zip',
#                          'path': 'slic-python-master',}),                 # OPEN
# (2 download sources to same dir, compilation) + patch (at least for '__init__.py') needed
              '_zbar': ({'linux-fedora': ['zbar'],
                         'linux-ubuntu': ['python-zbar']},
                        {  'url': 'https://pypi.python.org/packages/source/z/zbar/zbar-0.10.tar.bz2',
                          'path': 'zbar-0.10',
                         #$ diff -Nau --exclude="*.pyc" TEST__zbar/ _zbar/ > patch-zbar
                         'patch': 'patch-zbar'},
                        {}),                                               # OK
# TODO: vvv (include)
#               'TEST__bob': ({},
#                        {  'url': 'https://www.idiap.ch/software/bob/packages/bob-1.1.2.zip',
#                          'path': 'bob-1.1.2',
#                         #$ diff -Nau --exclude="*.pyc" TEST__bob/ _bob/ > patch-bob
#                         'patch': 'patch-bob',},
#                        {}),                                               # OPEN
# (complex compilation) + patch (at least for '__init__.py') needed
#     'TEST_xbob_flandmark': ({},
#                        {  'url': 'https://pypi.python.org/packages/source/x/xbob.flandmark/xbob.flandmark-1.0.9.zip',
#                          'path': 'xbob.flandmark-1.0.9',},
#                         #'patch': '',},
#                        {}),                                               # OPEN
# (complex compilation, dependent on '_bob') + patch (at least for '__init__.py') needed
}

modules_order = ['crontab', 'odf', 'openpyxl', 'BeautifulSoup.py', 'irclib',
                 'mwparserfromhell', 'colormath', 'jseg', 'jseg/jpeg-6b',
                 '_mlpy', '_music21', '_ocropus', 'opencv/haarcascades',
                 'pydmtx', 'py_w3c', '_zbar', ]
# OPEN: 'opencv', 'slic', '_bob', 'xbob_flandmark',

_patch_permission = None


import os
import sys
import inspect
import wikipedia as pywikibot   # sets externals path
#from pywikibot.comms import http

# allow imports from externals
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


### BEGIN of VisTrails inspired and copied code ### ### ### ### ### ### ### ###

def has_logger():
    #return hasattr(sys.modules['wikipedia'], 'logger')
    return hasattr(pywikibot, 'logger')


# TODO: solve properly because this is just a work-a-round, because module
# externals get imported in wikipedia.py before logger is setup properly, which
# should be changed! (meanwhile this is acceptable because code here should be
# executed once only...)
def lowlevel_warning(text):
    if has_logger():
        pywikibot.warning(text)
    else:
        print "WARNING:", text


def guess_system():
    import platform
    return ("%s-%s" % (platform.system(), platform.dist()[0])).lower()


def show_question(module):
    lowlevel_warning("Required package missing: %s\n"
                     "This package is not installed, but required by the file"
                     " '%s'." % (module, inspect.stack()[2][1]))
    lowlevel_warning("For more and additional information, please confer:\n"
                     "http://www.mediawiki.org/wiki/Manual:Pywikipediabot/"
                     "Installation#Dependencies")
    options = [(i+1) for i, item in enumerate(modules_needed[module]) if item]
    options += [0, 's', '']
    options.sort()
    options_msg = ("There are multiple ways to solve this:\n"
    "RECOMMENDED for     admins: always option [0] or the next available"
    " (e.g. [1])\n"
    "RECOMMENDED for non-admins: always option [2] (if available)\n"
    "0: automatically determine the best of the following methods (may need\n"
    "   administrator privileges)\n")
    if 1 in options:
        options_msg += ("1: install the package using the OS package"
                        " management system like yum\n"
                        "   or apt (needs administrator privileges)\n")
    if 2 in options:
        options_msg += ("2: download the package from its source URL and"
                        " install it locally into\n"
                        "   the pywikipedia package externals directory\n")
    if 3 in options:
        options_msg += ("3: download the package from its mercurial repo and"
                        " install it locally into\n"
                        "   the pywikipedia package externals directory\n")
    options_msg += "s: SKIP and solve manually"
    lowlevel_warning(options_msg)
    v = None
    while (v not in options):
        lowlevel_warning("Please choose [%s, s - default]: " % 
                           (", ".join(map(str, options[:-2]))))
        v = raw_input().lower()
        try:
            v = int(v)
        except:
            pass
    return v

def show_patch_question():
    global _patch_permission
    if _patch_permission is None:
        lowlevel_warning("Give externals permission to execute the patch command?"
                         " [y(es), n(o) - default]: ")
        v = raw_input().upper()
        _patch_permission = (v == 'Y') or (v == 'YES')
    return _patch_permission


def python_module_exists(module_name):
    """python_module_exists(module_name): Boolean.
Returns if python module of given name can be safely imported."""

    module_name = module_name.replace(u'.py', u'')
    module_name = module_name[1:] if module_name[0] == u'_' else module_name

    try:
        sys.modules[module_name]
        return True
    except KeyError:
        pass
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def linux_ubuntu_install(package_name):
    cmd = 'apt-get install -y'

    if type(package_name) == str:
        cmd += ' ' + package_name
    elif type(package_name) == list:
        for package in package_name:
            if type(package) != str:
                raise TypeError("Expected string or list of strings")
            cmd += ' ' + package

    sucmd = "sudo %s" % cmd
    result = os.system(sucmd)
    return (result == 0)  # 0 indicates success


def linux_fedora_install(package_name):
    cmd = 'yum -y install'

    if type(package_name) == str:
        cmd += ' ' + package_name
    elif type(package_name) == list:
        for package in package_name:
            if type(package) != str:
                raise TypeError("Expected string or list of strings")
            cmd += ' ' + package

    sucmd = "su -c'%s'" % cmd
    result = os.system(sucmd)
    return (result == 0)


def linux_install(dependency_dictionary):
    """Tries to import a python module. If unsuccessful, tries to install
the appropriate bundle and then reimport. py_import tries to be smart
about which system it runs on."""

    # Ugly fix to avoid circular import
    distro = guess_system()
    if not distro in dependency_dictionary:
        return False
    else:
        files = dependency_dictionary[distro]
        lowlevel_warning('Installing package(s) "%s"' % files)
        func = distro.replace('-', '_') + '_install'
        lowlevel_warning("Externals will need administrator privileges, and"
                         " you might get asked for the administrator"
                         " password. This prompt can be skipped with [Ctrl]+"
                         "[c] or [Enter].")
        if files and (func in globals()):
            callable_ = globals()[func]
            return callable_(files)
        else:
            return False


def sunos_install(dependency_dictionary):
    lowlevel_warning(u'Not implemented yet, use download mode (2) instead.')
    return False    # skip this in order to trigger 'download_install' next


def windows_install(dependency_dictionary):
    lowlevel_warning(u'Not available in windows OS, use download mode (2) instead.')
    return False    # skip this in order to trigger 'download_install' next

### END of VisTrails inspired and copied code   ### ### ### ### ### ### ### ###


def download_install(package, module, path):
    if package:
        lowlevel_warning(u'Download package "%s" from %s'
                         % (module, package['url']))
        import mimetypes
        import urllib2
        for i in range(3):
            response = urllib2.urlopen(package['url'])
            #response = http.request(pywikibot.getSite(), package['url'],
            #                        no_hostname = True, back_response = True)[0]
            if 'Content-Length' in response.headers:
                break
            lowlevel_warning(u'Could not retrieve data, re-trying ...')
        lowlevel_warning(u'Size of download: %s byte(s)'
                         % response.headers['Content-Length'])
        #mime = response.headers['Content-Type'].lower().split('/')
        mime = mimetypes.guess_type(package['url'],
                                    strict=True)[0].lower().split('/')
        lowlevel_warning(u'MIME type: %s' % mime)

        lowlevel_warning(u'Extract package "%s" to %s.'
                         % (module, os.path.join(path, module)))
        if len(mime) > 1:
            import StringIO
            if mime[1] in ['zip', 'x-zip-compressed']:
                import zipfile
                arch = zipfile.ZipFile(StringIO.StringIO(response.read()))
            elif mime[1] == 'x-tar':
                import tarfile
                arch = tarfile.open(fileobj=StringIO.StringIO(response.read()))
            else:
                raise NotImplementedError(u'Not implemented mime type %s'
                                          % mime[1])
            arch.extractall(os.path.join(path, '__setup_tmp/'))
            arch.close()
            import shutil
            shutil.move(os.path.join(path, '__setup_tmp/', package['path']),
                        os.path.join(path, module))
            shutil.rmtree(os.path.join(path, '__setup_tmp/'))

            result = 0
            if ('patch' in package) and show_patch_question():
                lowlevel_warning(u'Applying patch to %s in order to finish'
                                 u'installation of package "%s".'
                                 % (os.path.join(path, module), module))
                if sys.platform == 'win32':
                    cmd = '%s -p0 -d %s -i %s --binary' \
                          % (os.path.join(path, 'patch.exe'), path,
                             os.path.join(path, package['patch']))
                else:              # unix/linux, (mac too?)
                    cmd = '%s -p0 -d %s < %s' \
                          % ('patch', path,
                             os.path.join(path, package['patch']))
                result = os.system(cmd)

            lowlevel_warning(u'Package "%s" installed to %s.'
                             % (module, os.path.join(path, module)))
            return (result == 0)


def mercurial_repo_install(package, module, path):
    if package:
        cmd = 'hg clone'
        lowlevel_warning(u'Mercurial clone "%s" from %s'
                         % (module, package['url']))
        cmd += " -r %s %s %s" % (package['rev'], package['url'],
                                 os.path.join(path, module))
        result = os.system(cmd)
        return (result == 0)


def check_setup(m):
    path = os.path.dirname(os.path.abspath(os.path.join(os.curdir, __file__)))
    mf = os.path.join(path, m)

    # search missing module
    if python_module_exists(m):
        return
    if os.path.exists(mf):
        return

    sel = show_question(m)

    # install the missing module
    dist = guess_system()
    func = dist.split(u'-')[0] + '_install'
    if sel in [0, 1]:
        lowlevel_warning(u'(1) Trying to install by use of "%s" package management system:' % dist)
        if (func in globals()) and globals()[func](modules_needed[m][0]):
            return
    if sel in [0, 2]:
        lowlevel_warning(u'(2) Trying to install by download from source URL:')
        if download_install(modules_needed[m][1], m, path):
            return
    if sel in [0, 3]:
        lowlevel_warning(u'(3) Trying to install by use of mercurial:')
        if (len(modules_needed[m]) > 2) and\
           mercurial_repo_install(modules_needed[m][2], m, path):
            return
    if sel in [0, 1, 2, 3]:
        lowlevel_warning(u'No suitable package could be found nor installed!')

    lowlevel_warning(u'Several scripts might fail, if the modules are not'
                     u' installed as needed! You can either install them'
                     u' by yourself to the system or extract them into the'
                     u' externals/ directory. If you do not install them, this'
                     u' script will ask you again next time when executed.')


def check_setup_all():
    for m in modules_order:
        check_setup(m)


# check and install modules NEEDED
if sys.platform == 'win32':
    check_setup('patch.exe')
#check_setup('BeautifulSoup.py')
#check_setup('mwparserfromhell')
