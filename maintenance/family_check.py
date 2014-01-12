# -*- coding: utf-8  -*-
#
# (C) xqt, 2011, 2013
# (C) Pywikipedia bot team, 2003-2009
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import sys
sys.path.insert(1, '..')

import wikipedia, config, query

def check_namespaces(site):
    try:
        if not site.apipath():
            wikipedia.output(u'Warning! %s has no apipath() defined!' % site)
            return
    except NotImplementedError:
        wikipedia.output(u'Warning! %s is not support API!' % site)
        return
    result = []
    for namespace in site.siteinfo('namespaces').itervalues():
        ns = namespace['id']
        defined = set()
        default_namespace = None
        defined_namespace = None
        try:
            default_namespace = site.family.namespaces[ns]['_default']
        except KeyError:
            wikipedia.output(u'Warning! %s has no _default for namespace %s'
                             % (site, ns))

        if default_namespace:
            if isinstance(default_namespace, basestring):
                default_namespace = [default_namespace]
            defined = set(default_namespace)
            try:
                defined_namespace = site.family.namespaces[ns][site.lang]
            except KeyError:
                wikipedia.output(u'Warning! %s has only _default for namespace '
                                 u'%s' % (site, ns))
                defined_namespace = default_namespace[:]
            else:
                if isinstance(defined_namespace, basestring):
                    defined.add(defined_namespace)
                    defined_namespace = [defined_namespace]
                else:
                    defined = defined.union(set(defined_namespace))

        aliases = set([namespace['*']]) if namespace['*'] else set()
        if 'canonical' in namespace:
            aliases.add(namespace['canonical'])
        for alias in site.siteinfo('namespacealiases'):
            if alias['id'] == ns:
                aliases.add(alias['*'])

        if aliases and aliases <> defined:
            result.append((ns, [namespace['*']],
                           defined_namespace))

    for namespace in site.siteinfo('namespacealiases'):
        ns =  namespace['id']
        for alias in result:
            if alias[0] == ns:
                try:
                    default = site.family.namespace('_default', ns, all=True)
                except KeyError:
                    pass
                else:
                    if not namespace['*'] in default:
                        if namespace['*'] in alias[1]:
                            raise
                        else:
                            alias[1].append(namespace['*'])
    return result

def check_family(family):
    wikipedia.output(u'Checking namespaces for %s' % family.name)
    result = {}
    for lang in family.langs:
        if not lang in family.obsolete:
            site = wikipedia.getSite(lang, family)
            wikipedia.output(u'Checking %s' % site)
            namespaces = check_namespaces(site)
            if namespaces:
                for id, name, defined_namespace in namespaces:
                    try:
                        msg = u'Namespace %s for %s is ' \
                              + (u'[%s]. ' if len(name) > 1 else u'%s. ') \
                              + (u'[%s]' if len(defined_namespace) > 1 else u'%s') \
                              + u' is defined in family file.'
                        wikipedia.output(msg % (id, site,
                                                ', '.join(name),
                                                ', '.join(defined_namespace)))
                    except:
                        pass
                result[lang] = namespaces
    return result

if __name__ == '__main__':
    try:
        wikipedia.handleArgs()
        family = wikipedia.Family(wikipedia.default_family)
        result = check_family(family)
        wikipedia.output(u'\nWriting raw Python dictionary to stdout.')
        wikipedia.output(u'Format is: (namespace_id, namespace_name, predefined_namespace)')
        print
        print result
    finally:
        wikipedia.stopme()
