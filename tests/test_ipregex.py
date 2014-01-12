#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit test framework for ip_regexp"""
__version__ = '$Id$'

import unittest
import test_utils
from tests.test_pywiki import PyWikiTestCase
import wikipedia as pywikibot
from userlib import ip_regexp

total = 0
fail = 0

class PyWikiIpRegexCase(PyWikiTestCase):
    
    def ipv6test(self, result, IP):
        global total, fail
        total += 1
        try:
            test = self.assertEqual(bool(result), bool(ip_regexp.match(IP)))
        except AssertionError:
            fail += 1
            test = True
        if test:
            print '"%s" should match %s - not OK' % (IP, bool(result))
        else:
            return
            print '"%s" match %s - OK' % (IP, bool(result))
        
    def test_IP(self):
        # test from http://download.dartware.com/thirdparty/test-ipv6-regex.pl
        self.ipv6test(not 1, "");# empty string 
        self.ipv6test(1, "::1");# loopback, compressed, non-routable 
        self.ipv6test(1, "::");# unspecified, compressed, non-routable 
        self.ipv6test(1, "0:0:0:0:0:0:0:1");# loopback, full 
        self.ipv6test(1, "0:0:0:0:0:0:0:0");# unspecified, full 
        self.ipv6test(1, "2001:DB8:0:0:8:800:200C:417A");# unicast, full 
        self.ipv6test(1, "FF01:0:0:0:0:0:0:101");# multicast, full 
        self.ipv6test(1, "2001:DB8::8:800:200C:417A");# unicast, compressed 
        self.ipv6test(1, "FF01::101");# multicast, compressed 
        self.ipv6test(not 1, "2001:DB8:0:0:8:800:200C:417A:221");# unicast, full 
        self.ipv6test(not 1, "FF01::101::2");# multicast, compressed 
        self.ipv6test(1, "fe80::217:f2ff:fe07:ed62");

        self.ipv6test(1, "2001:0000:1234:0000:0000:C1C0:ABCD:0876");
        self.ipv6test(1, "3ffe:0b00:0000:0000:0001:0000:0000:000a");
        self.ipv6test(1, "FF02:0000:0000:0000:0000:0000:0000:0001");
        self.ipv6test(1, "0000:0000:0000:0000:0000:0000:0000:0001");
        self.ipv6test(1, "0000:0000:0000:0000:0000:0000:0000:0000");
        self.ipv6test(not 1, "02001:0000:1234:0000:0000:C1C0:ABCD:0876");	# extra 0 not allowed! 
        self.ipv6test(not 1, "2001:0000:1234:0000:00001:C1C0:ABCD:0876");	# extra 0 not allowed! 
        #self.ipv6test(1, " 2001:0000:1234:0000:0000:C1C0:ABCD:0876");		# leading space
        #self.ipv6test(1, "2001:0000:1234:0000:0000:C1C0:ABCD:0876");		# trailing space
        #self.ipv6test(1, " 2001:0000:1234:0000:0000:C1C0:ABCD:0876  ");	# leading and trailing space
        self.ipv6test(not 1, "2001:0000:1234:0000:0000:C1C0:ABCD:0876  0");	# junk after valid address
        self.ipv6test(not 1, "2001:0000:1234: 0000:0000:C1C0:ABCD:0876");	# internal space

        self.ipv6test(not 1, "3ffe:0b00:0000:0001:0000:0000:000a");			# seven segments
        self.ipv6test(not 1, "FF02:0000:0000:0000:0000:0000:0000:0000:0001");	# nine segments
        self.ipv6test(not 1, "3ffe:b00::1::a");								# double "::"
        self.ipv6test(not 1, "::1111:2222:3333:4444:5555:6666::");			# double "::"
        self.ipv6test(1, "2::10");
        self.ipv6test(1, "ff02::1");
        self.ipv6test(1, "fe80::");
        self.ipv6test(1, "2002::");
        self.ipv6test(1, "2001:db8::");
        self.ipv6test(1, "2001:0db8:1234::");
        self.ipv6test(1, "::ffff:0:0");
        self.ipv6test(1, "::1");
        self.ipv6test(1, "1:2:3:4:5:6:7:8");
        self.ipv6test(1, "1:2:3:4:5:6::8");
        self.ipv6test(1, "1:2:3:4:5::8");
        self.ipv6test(1, "1:2:3:4::8");
        self.ipv6test(1, "1:2:3::8");
        self.ipv6test(1, "1:2::8");
        self.ipv6test(1, "1::8");
        self.ipv6test(1, "1::2:3:4:5:6:7");
        self.ipv6test(1, "1::2:3:4:5:6");
        self.ipv6test(1, "1::2:3:4:5");
        self.ipv6test(1, "1::2:3:4");
        self.ipv6test(1, "1::2:3");
        self.ipv6test(1, "1::8");
        self.ipv6test(1, "::2:3:4:5:6:7:8");
        self.ipv6test(1, "::2:3:4:5:6:7");
        self.ipv6test(1, "::2:3:4:5:6");
        self.ipv6test(1, "::2:3:4:5");
        self.ipv6test(1, "::2:3:4");
        self.ipv6test(1, "::2:3");
        self.ipv6test(1, "::8");
        self.ipv6test(1, "1:2:3:4:5:6::");
        self.ipv6test(1, "1:2:3:4:5::");
        self.ipv6test(1, "1:2:3:4::");
        self.ipv6test(1, "1:2:3::");
        self.ipv6test(1, "1:2::");
        self.ipv6test(1, "1::");
        self.ipv6test(1, "1:2:3:4:5::7:8");
        self.ipv6test(not 1, "1:2:3::4:5::7:8");							# Double "::"
        self.ipv6test(not 1, "12345::6:7:8");
        self.ipv6test(1, "1:2:3:4::7:8");
        self.ipv6test(1, "1:2:3::7:8");
        self.ipv6test(1, "1:2::7:8");
        self.ipv6test(1, "1::7:8");

        # IPv4 addresses as dotted-quads
        self.ipv6test(1, "1:2:3:4:5:6:1.2.3.4");
        self.ipv6test(1, "1:2:3:4:5::1.2.3.4");
        self.ipv6test(1, "1:2:3:4::1.2.3.4");
        self.ipv6test(1, "1:2:3::1.2.3.4");
        self.ipv6test(1, "1:2::1.2.3.4");
        self.ipv6test(1, "1::1.2.3.4");
        self.ipv6test(1, "1:2:3:4::5:1.2.3.4");
        self.ipv6test(1, "1:2:3::5:1.2.3.4");
        self.ipv6test(1, "1:2::5:1.2.3.4");
        self.ipv6test(1, "1::5:1.2.3.4");
        self.ipv6test(1, "1::5:11.22.33.44");
        self.ipv6test(not 1, "1::5:400.2.3.4");
        self.ipv6test(not 1, "1::5:260.2.3.4");
        self.ipv6test(not 1, "1::5:256.2.3.4");
        self.ipv6test(not 1, "1::5:1.256.3.4");
        self.ipv6test(not 1, "1::5:1.2.256.4");
        self.ipv6test(not 1, "1::5:1.2.3.256");
        self.ipv6test(not 1, "1::5:300.2.3.4");
        self.ipv6test(not 1, "1::5:1.300.3.4");
        self.ipv6test(not 1, "1::5:1.2.300.4");
        self.ipv6test(not 1, "1::5:1.2.3.300");
        self.ipv6test(not 1, "1::5:900.2.3.4");
        self.ipv6test(not 1, "1::5:1.900.3.4");
        self.ipv6test(not 1, "1::5:1.2.900.4");
        self.ipv6test(not 1, "1::5:1.2.3.900");
        self.ipv6test(not 1, "1::5:300.300.300.300");
        self.ipv6test(not 1, "1::5:3000.30.30.30");
        self.ipv6test(not 1, "1::400.2.3.4");
        self.ipv6test(not 1, "1::260.2.3.4");
        self.ipv6test(not 1, "1::256.2.3.4");
        self.ipv6test(not 1, "1::1.256.3.4");
        self.ipv6test(not 1, "1::1.2.256.4");
        self.ipv6test(not 1, "1::1.2.3.256");
        self.ipv6test(not 1, "1::300.2.3.4");
        self.ipv6test(not 1, "1::1.300.3.4");
        self.ipv6test(not 1, "1::1.2.300.4");
        self.ipv6test(not 1, "1::1.2.3.300");
        self.ipv6test(not 1, "1::900.2.3.4");
        self.ipv6test(not 1, "1::1.900.3.4");
        self.ipv6test(not 1, "1::1.2.900.4");
        self.ipv6test(not 1, "1::1.2.3.900");
        self.ipv6test(not 1, "1::300.300.300.300");
        self.ipv6test(not 1, "1::3000.30.30.30");
        self.ipv6test(not 1, "::400.2.3.4");
        self.ipv6test(not 1, "::260.2.3.4");
        self.ipv6test(not 1, "::256.2.3.4");
        self.ipv6test(not 1, "::1.256.3.4");
        self.ipv6test(not 1, "::1.2.256.4");
        self.ipv6test(not 1, "::1.2.3.256");
        self.ipv6test(not 1, "::300.2.3.4");
        self.ipv6test(not 1, "::1.300.3.4");
        self.ipv6test(not 1, "::1.2.300.4");
        self.ipv6test(not 1, "::1.2.3.300");
        self.ipv6test(not 1, "::900.2.3.4");
        self.ipv6test(not 1, "::1.900.3.4");
        self.ipv6test(not 1, "::1.2.900.4");
        self.ipv6test(not 1, "::1.2.3.900");
        self.ipv6test(not 1, "::300.300.300.300");
        self.ipv6test(not 1, "::3000.30.30.30");
        self.ipv6test(1, "fe80::217:f2ff:254.7.237.98");
        self.ipv6test(1, "::ffff:192.168.1.26");
        self.ipv6test(not 1, "2001:1:1:1:1:1:255Z255X255Y255");				# garbage instead of "." in IPv4
        self.ipv6test(not 1, "::ffff:192x168.1.26");							# ditto
        self.ipv6test(1, "::ffff:192.168.1.1");
        self.ipv6test(1, "0:0:0:0:0:0:13.1.68.3");# IPv4-compatible IPv6 address, full, deprecated 
        self.ipv6test(1, "0:0:0:0:0:FFFF:129.144.52.38");# IPv4-mapped IPv6 address, full 
        self.ipv6test(1, "::13.1.68.3");# IPv4-compatible IPv6 address, compressed, deprecated 
        self.ipv6test(1, "::FFFF:129.144.52.38");# IPv4-mapped IPv6 address, compressed 
        self.ipv6test(1, "fe80:0:0:0:204:61ff:254.157.241.86");
        self.ipv6test(1, "fe80::204:61ff:254.157.241.86");
        self.ipv6test(1, "::ffff:12.34.56.78");
        self.ipv6test(not 1, "::ffff:2.3.4");
        self.ipv6test(not 1, "::ffff:257.1.2.3");
        self.ipv6test(not 1, "1.2.3.4");

        self.ipv6test(not 1, "1.2.3.4:1111:2222:3333:4444::5555");  # Aeron
        self.ipv6test(not 1, "1.2.3.4:1111:2222:3333::5555");
        self.ipv6test(not 1, "1.2.3.4:1111:2222::5555");
        self.ipv6test(not 1, "1.2.3.4:1111::5555");
        self.ipv6test(not 1, "1.2.3.4::5555");
        self.ipv6test(not 1, "1.2.3.4::");

        # Testing IPv4 addresses represented as dotted-quads
        # Leading zero's in IPv4 addresses not allowed: some systems treat the leading "0" in ".086" as the start of an octal number
        # Update: The BNF in RFC-3986 explicitly defines the dec-octet (for IPv4 addresses) not to have a leading zero
        self.ipv6test(not 1, "fe80:0000:0000:0000:0204:61ff:254.157.241.086");
        self.ipv6test(1, "::ffff:192.0.2.128");   # but this is OK, since there's a single digit
        self.ipv6test(not 1, "XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:00.00.00.00");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:000.000.000.000");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:256.256.256.256");

        # Not testing address with subnet mask
        # self.ipv6test(1, "2001:0DB8:0000:CD30:0000:0000:0000:0000/60");# full, with prefix 
        # self.ipv6test(1, "2001:0DB8::CD30:0:0:0:0/60");# compressed, with prefix 
        # self.ipv6test(1, "2001:0DB8:0:CD30::/60");# compressed, with prefix #2 
        # self.ipv6test(1, "::/128");# compressed, unspecified address type, non-routable 
        # self.ipv6test(1, "::1/128");# compressed, loopback address type, non-routable 
        # self.ipv6test(1, "FF00::/8");# compressed, multicast address type 
        # self.ipv6test(1, "FE80::/10");# compressed, link-local unicast, non-routable 
        # self.ipv6test(1, "FEC0::/10");# compressed, site-local unicast, deprecated 
        # self.ipv6test(not 1, "124.15.6.89/60");# standard IPv4, prefix not allowed 

        self.ipv6test(1, "fe80:0000:0000:0000:0204:61ff:fe9d:f156");
        self.ipv6test(1, "fe80:0:0:0:204:61ff:fe9d:f156");
        self.ipv6test(1, "fe80::204:61ff:fe9d:f156");
        self.ipv6test(1, "::1");
        self.ipv6test(1, "fe80::");
        self.ipv6test(1, "fe80::1");
        self.ipv6test(not 1, ":");
        self.ipv6test(1, "::ffff:c000:280");

        # Aeron supplied these test cases
        self.ipv6test(not 1, "1111:2222:3333:4444::5555:");
        self.ipv6test(not 1, "1111:2222:3333::5555:");
        self.ipv6test(not 1, "1111:2222::5555:");
        self.ipv6test(not 1, "1111::5555:");
        self.ipv6test(not 1, "::5555:");
        self.ipv6test(not 1, ":::");
        self.ipv6test(not 1, "1111:");
        self.ipv6test(not 1, ":");

        self.ipv6test(not 1, ":1111:2222:3333:4444::5555");
        self.ipv6test(not 1, ":1111:2222:3333::5555");
        self.ipv6test(not 1, ":1111:2222::5555");
        self.ipv6test(not 1, ":1111::5555");
        self.ipv6test(not 1, ":::5555");
        self.ipv6test(not 1, ":::");


        # Additional test cases
        # from http://rt.cpan.org/Public/Bug/Display.html?id=50693

        self.ipv6test(1, "2001:0db8:85a3:0000:0000:8a2e:0370:7334");
        self.ipv6test(1, "2001:db8:85a3:0:0:8a2e:370:7334");
        self.ipv6test(1, "2001:db8:85a3::8a2e:370:7334");
        self.ipv6test(1, "2001:0db8:0000:0000:0000:0000:1428:57ab");
        self.ipv6test(1, "2001:0db8:0000:0000:0000::1428:57ab");
        self.ipv6test(1, "2001:0db8:0:0:0:0:1428:57ab");
        self.ipv6test(1, "2001:0db8:0:0::1428:57ab");
        self.ipv6test(1, "2001:0db8::1428:57ab");
        self.ipv6test(1, "2001:db8::1428:57ab");
        self.ipv6test(1, "0000:0000:0000:0000:0000:0000:0000:0001");
        self.ipv6test(1, "::1");
        self.ipv6test(1, "::ffff:0c22:384e");
        self.ipv6test(1, "2001:0db8:1234:0000:0000:0000:0000:0000");
        self.ipv6test(1, "2001:0db8:1234:ffff:ffff:ffff:ffff:ffff");
        self.ipv6test(1, "2001:db8:a::123");
        self.ipv6test(1, "fe80::");

        self.ipv6test(not 1, "123");
        self.ipv6test(not 1, "ldkfj");
        self.ipv6test(not 1, "2001::FFD3::57ab");
        self.ipv6test(not 1, "2001:db8:85a3::8a2e:37023:7334");
        self.ipv6test(not 1, "2001:db8:85a3::8a2e:370k:7334");
        self.ipv6test(not 1, "1:2:3:4:5:6:7:8:9");
        self.ipv6test(not 1, "1::2::3");
        self.ipv6test(not 1, "1:::3:4:5");
        self.ipv6test(not 1, "1:2:3::4:5:6:7:8:9");

        # New from Aeron 
        self.ipv6test(1, "1111:2222:3333:4444:5555:6666:7777:8888");
        self.ipv6test(1, "1111:2222:3333:4444:5555:6666:7777::");
        self.ipv6test(1, "1111:2222:3333:4444:5555:6666::");
        self.ipv6test(1, "1111:2222:3333:4444:5555::");
        self.ipv6test(1, "1111:2222:3333:4444::");
        self.ipv6test(1, "1111:2222:3333::");
        self.ipv6test(1, "1111:2222::");
        self.ipv6test(1, "1111::");
        # self.ipv6test(1, "::");     #duplicate
        self.ipv6test(1, "1111:2222:3333:4444:5555:6666::8888");
        self.ipv6test(1, "1111:2222:3333:4444:5555::8888");
        self.ipv6test(1, "1111:2222:3333:4444::8888");
        self.ipv6test(1, "1111:2222:3333::8888");
        self.ipv6test(1, "1111:2222::8888");
        self.ipv6test(1, "1111::8888");
        self.ipv6test(1, "::8888");
        self.ipv6test(1, "1111:2222:3333:4444:5555::7777:8888");
        self.ipv6test(1, "1111:2222:3333:4444::7777:8888");
        self.ipv6test(1, "1111:2222:3333::7777:8888");
        self.ipv6test(1, "1111:2222::7777:8888");
        self.ipv6test(1, "1111::7777:8888");
        self.ipv6test(1, "::7777:8888");
        self.ipv6test(1, "1111:2222:3333:4444::6666:7777:8888");
        self.ipv6test(1, "1111:2222:3333::6666:7777:8888");
        self.ipv6test(1, "1111:2222::6666:7777:8888");
        self.ipv6test(1, "1111::6666:7777:8888");
        self.ipv6test(1, "::6666:7777:8888");
        self.ipv6test(1, "1111:2222:3333::5555:6666:7777:8888");
        self.ipv6test(1, "1111:2222::5555:6666:7777:8888");
        self.ipv6test(1, "1111::5555:6666:7777:8888");
        self.ipv6test(1, "::5555:6666:7777:8888");
        self.ipv6test(1, "1111:2222::4444:5555:6666:7777:8888");
        self.ipv6test(1, "1111::4444:5555:6666:7777:8888");
        self.ipv6test(1, "::4444:5555:6666:7777:8888");
        self.ipv6test(1, "1111::3333:4444:5555:6666:7777:8888");
        self.ipv6test(1, "::3333:4444:5555:6666:7777:8888");
        self.ipv6test(1, "::2222:3333:4444:5555:6666:7777:8888");
        self.ipv6test(1, "1111:2222:3333:4444:5555:6666:123.123.123.123");
        self.ipv6test(1, "1111:2222:3333:4444:5555::123.123.123.123");
        self.ipv6test(1, "1111:2222:3333:4444::123.123.123.123");
        self.ipv6test(1, "1111:2222:3333::123.123.123.123");
        self.ipv6test(1, "1111:2222::123.123.123.123");
        self.ipv6test(1, "1111::123.123.123.123");
        self.ipv6test(1, "::123.123.123.123");
        self.ipv6test(1, "1111:2222:3333:4444::6666:123.123.123.123");
        self.ipv6test(1, "1111:2222:3333::6666:123.123.123.123");
        self.ipv6test(1, "1111:2222::6666:123.123.123.123");
        self.ipv6test(1, "1111::6666:123.123.123.123");
        self.ipv6test(1, "::6666:123.123.123.123");
        self.ipv6test(1, "1111:2222:3333::5555:6666:123.123.123.123");
        self.ipv6test(1, "1111:2222::5555:6666:123.123.123.123");
        self.ipv6test(1, "1111::5555:6666:123.123.123.123");
        self.ipv6test(1, "::5555:6666:123.123.123.123");
        self.ipv6test(1, "1111:2222::4444:5555:6666:123.123.123.123");
        self.ipv6test(1, "1111::4444:5555:6666:123.123.123.123");
        self.ipv6test(1, "::4444:5555:6666:123.123.123.123");
        self.ipv6test(1, "1111::3333:4444:5555:6666:123.123.123.123");
        self.ipv6test(1, "::2222:3333:4444:5555:6666:123.123.123.123");

        # Playing with combinations of "0" and "::"
        # NB: these are all sytactically correct, but are bad form 
        #   because "0" adjacent to "::" should be combined into "::"
        self.ipv6test(1, "::0:0:0:0:0:0:0");
        self.ipv6test(1, "::0:0:0:0:0:0");
        self.ipv6test(1, "::0:0:0:0:0");
        self.ipv6test(1, "::0:0:0:0");
        self.ipv6test(1, "::0:0:0");
        self.ipv6test(1, "::0:0");
        self.ipv6test(1, "::0");
        self.ipv6test(1, "0:0:0:0:0:0:0::");
        self.ipv6test(1, "0:0:0:0:0:0::");
        self.ipv6test(1, "0:0:0:0:0::");
        self.ipv6test(1, "0:0:0:0::");
        self.ipv6test(1, "0:0:0::");
        self.ipv6test(1, "0:0::");
        self.ipv6test(1, "0::");

        # New invalid from Aeron
        # Invalid data
        self.ipv6test(not 1, "XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX");

        # Too many components
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777:8888:9999");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777:8888::");
        self.ipv6test(not 1, "::2222:3333:4444:5555:6666:7777:8888:9999");

        # Too few components
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555");
        self.ipv6test(not 1, "1111:2222:3333:4444");
        self.ipv6test(not 1, "1111:2222:3333");
        self.ipv6test(not 1, "1111:2222");
        self.ipv6test(not 1, "1111");

        # Missing :
        self.ipv6test(not 1, "11112222:3333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, "1111:22223333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, "1111:2222:33334444:5555:6666:7777:8888");
        self.ipv6test(not 1, "1111:2222:3333:44445555:6666:7777:8888");
        self.ipv6test(not 1, "1111:2222:3333:4444:55556666:7777:8888");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:66667777:8888");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:77778888");

        # Missing : intended for ::
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777:8888:");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777:");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:");
        self.ipv6test(not 1, "1111:2222:3333:4444:");
        self.ipv6test(not 1, "1111:2222:3333:");
        self.ipv6test(not 1, "1111:2222:");
        self.ipv6test(not 1, "1111:");
        self.ipv6test(not 1, ":");
        self.ipv6test(not 1, ":8888");
        self.ipv6test(not 1, ":7777:8888");
        self.ipv6test(not 1, ":6666:7777:8888");
        self.ipv6test(not 1, ":5555:6666:7777:8888");
        self.ipv6test(not 1, ":4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":3333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":2222:3333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555:6666:7777:8888");

        # :::
        self.ipv6test(not 1, ":::2222:3333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, "1111:::3333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, "1111:2222:::4444:5555:6666:7777:8888");
        self.ipv6test(not 1, "1111:2222:3333:::5555:6666:7777:8888");
        self.ipv6test(not 1, "1111:2222:3333:4444:::6666:7777:8888");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:::7777:8888");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:::8888");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777:::");

        # Double ::");
        self.ipv6test(not 1, "::2222::4444:5555:6666:7777:8888");
        self.ipv6test(not 1, "::2222:3333::5555:6666:7777:8888");
        self.ipv6test(not 1, "::2222:3333:4444::6666:7777:8888");
        self.ipv6test(not 1, "::2222:3333:4444:5555::7777:8888");
        self.ipv6test(not 1, "::2222:3333:4444:5555:7777::8888");
        self.ipv6test(not 1, "::2222:3333:4444:5555:7777:8888::");

        self.ipv6test(not 1, "1111::3333::5555:6666:7777:8888");
        self.ipv6test(not 1, "1111::3333:4444::6666:7777:8888");
        self.ipv6test(not 1, "1111::3333:4444:5555::7777:8888");
        self.ipv6test(not 1, "1111::3333:4444:5555:6666::8888");
        self.ipv6test(not 1, "1111::3333:4444:5555:6666:7777::");

        self.ipv6test(not 1, "1111:2222::4444::6666:7777:8888");
        self.ipv6test(not 1, "1111:2222::4444:5555::7777:8888");
        self.ipv6test(not 1, "1111:2222::4444:5555:6666::8888");
        self.ipv6test(not 1, "1111:2222::4444:5555:6666:7777::");

        self.ipv6test(not 1, "1111:2222:3333::5555::7777:8888");
        self.ipv6test(not 1, "1111:2222:3333::5555:6666::8888");
        self.ipv6test(not 1, "1111:2222:3333::5555:6666:7777::");

        self.ipv6test(not 1, "1111:2222:3333:4444::6666::8888");
        self.ipv6test(not 1, "1111:2222:3333:4444::6666:7777::");

        self.ipv6test(not 1, "1111:2222:3333:4444:5555::7777::");


        # Too many components"
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777:8888:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666::1.2.3.4");
        self.ipv6test(not 1, "::2222:3333:4444:5555:6666:7777:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:1.2.3.4.5");

        # Too few components
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:1.2.3.4");
        self.ipv6test(not 1, "1111:1.2.3.4");
        self.ipv6test(not 1, "1.2.3.4");

        # Missing :
        self.ipv6test(not 1, "11112222:3333:4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111:22223333:4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:33334444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:44445555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:55556666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:66661.2.3.4");

        # Missing .
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:255255.255.255");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:255.255255.255");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:255.255.255255");

        # Missing : intended for ::
        self.ipv6test(not 1, ":1.2.3.4");
        self.ipv6test(not 1, ":6666:1.2.3.4");
        self.ipv6test(not 1, ":5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":3333:4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":2222:3333:4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555:6666:1.2.3.4");

        # :::
        self.ipv6test(not 1, ":::2222:3333:4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111:::3333:4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:::4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:::5555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:::6666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:::1.2.3.4");

        # Double ::
        self.ipv6test(not 1, "::2222::4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, "::2222:3333::5555:6666:1.2.3.4");
        self.ipv6test(not 1, "::2222:3333:4444::6666:1.2.3.4");
        self.ipv6test(not 1, "::2222:3333:4444:5555::1.2.3.4");

        self.ipv6test(not 1, "1111::3333::5555:6666:1.2.3.4");
        self.ipv6test(not 1, "1111::3333:4444::6666:1.2.3.4");
        self.ipv6test(not 1, "1111::3333:4444:5555::1.2.3.4");

        self.ipv6test(not 1, "1111:2222::4444::6666:1.2.3.4");
        self.ipv6test(not 1, "1111:2222::4444:5555::1.2.3.4");

        self.ipv6test(not 1, "1111:2222:3333::5555::1.2.3.4");

        # Missing parts
        self.ipv6test(not 1, "::.");
        self.ipv6test(not 1, "::..");
        self.ipv6test(not 1, "::...");
        self.ipv6test(not 1, "::1...");
        self.ipv6test(not 1, "::1.2..");
        self.ipv6test(not 1, "::1.2.3.");
        self.ipv6test(not 1, "::.2..");
        self.ipv6test(not 1, "::.2.3.");
        self.ipv6test(not 1, "::.2.3.4");
        self.ipv6test(not 1, "::..3.");
        self.ipv6test(not 1, "::..3.4");
        self.ipv6test(not 1, "::...4");

        # Extra : in front
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555:6666:7777::");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555:6666::");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555::");
        self.ipv6test(not 1, ":1111:2222:3333:4444::");
        self.ipv6test(not 1, ":1111:2222:3333::");
        self.ipv6test(not 1, ":1111:2222::");
        self.ipv6test(not 1, ":1111::");
        self.ipv6test(not 1, ":::");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555:6666::8888");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555::8888");
        self.ipv6test(not 1, ":1111:2222:3333:4444::8888");
        self.ipv6test(not 1, ":1111:2222:3333::8888");
        self.ipv6test(not 1, ":1111:2222::8888");
        self.ipv6test(not 1, ":1111::8888");
        self.ipv6test(not 1, ":::8888");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555::7777:8888");
        self.ipv6test(not 1, ":1111:2222:3333:4444::7777:8888");
        self.ipv6test(not 1, ":1111:2222:3333::7777:8888");
        self.ipv6test(not 1, ":1111:2222::7777:8888");
        self.ipv6test(not 1, ":1111::7777:8888");
        self.ipv6test(not 1, ":::7777:8888");
        self.ipv6test(not 1, ":1111:2222:3333:4444::6666:7777:8888");
        self.ipv6test(not 1, ":1111:2222:3333::6666:7777:8888");
        self.ipv6test(not 1, ":1111:2222::6666:7777:8888");
        self.ipv6test(not 1, ":1111::6666:7777:8888");
        self.ipv6test(not 1, ":::6666:7777:8888");
        self.ipv6test(not 1, ":1111:2222:3333::5555:6666:7777:8888");
        self.ipv6test(not 1, ":1111:2222::5555:6666:7777:8888");
        self.ipv6test(not 1, ":1111::5555:6666:7777:8888");
        self.ipv6test(not 1, ":::5555:6666:7777:8888");
        self.ipv6test(not 1, ":1111:2222::4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":1111::4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":::4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":1111::3333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":::3333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":::2222:3333:4444:5555:6666:7777:8888");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":1111:2222:3333:4444:5555::1.2.3.4");
        self.ipv6test(not 1, ":1111:2222:3333:4444::1.2.3.4");
        self.ipv6test(not 1, ":1111:2222:3333::1.2.3.4");
        self.ipv6test(not 1, ":1111:2222::1.2.3.4");
        self.ipv6test(not 1, ":1111::1.2.3.4");
        self.ipv6test(not 1, ":::1.2.3.4");
        self.ipv6test(not 1, ":1111:2222:3333:4444::6666:1.2.3.4");
        self.ipv6test(not 1, ":1111:2222:3333::6666:1.2.3.4");
        self.ipv6test(not 1, ":1111:2222::6666:1.2.3.4");
        self.ipv6test(not 1, ":1111::6666:1.2.3.4");
        self.ipv6test(not 1, ":::6666:1.2.3.4");
        self.ipv6test(not 1, ":1111:2222:3333::5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":1111:2222::5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":1111::5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":::5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":1111:2222::4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":1111::4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":::4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":1111::3333:4444:5555:6666:1.2.3.4");
        self.ipv6test(not 1, ":::2222:3333:4444:5555:6666:1.2.3.4");

        # Extra : at end
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:7777:::");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666:::");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:::");
        self.ipv6test(not 1, "1111:2222:3333:4444:::");
        self.ipv6test(not 1, "1111:2222:3333:::");
        self.ipv6test(not 1, "1111:2222:::");
        self.ipv6test(not 1, "1111:::");
        self.ipv6test(not 1, ":::");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555:6666::8888:");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555::8888:");
        self.ipv6test(not 1, "1111:2222:3333:4444::8888:");
        self.ipv6test(not 1, "1111:2222:3333::8888:");
        self.ipv6test(not 1, "1111:2222::8888:");
        self.ipv6test(not 1, "1111::8888:");
        self.ipv6test(not 1, "::8888:");
        self.ipv6test(not 1, "1111:2222:3333:4444:5555::7777:8888:");
        self.ipv6test(not 1, "1111:2222:3333:4444::7777:8888:");
        self.ipv6test(not 1, "1111:2222:3333::7777:8888:");
        self.ipv6test(not 1, "1111:2222::7777:8888:");
        self.ipv6test(not 1, "1111::7777:8888:");
        self.ipv6test(not 1, "::7777:8888:");
        self.ipv6test(not 1, "1111:2222:3333:4444::6666:7777:8888:");
        self.ipv6test(not 1, "1111:2222:3333::6666:7777:8888:");
        self.ipv6test(not 1, "1111:2222::6666:7777:8888:");
        self.ipv6test(not 1, "1111::6666:7777:8888:");
        self.ipv6test(not 1, "::6666:7777:8888:");
        self.ipv6test(not 1, "1111:2222:3333::5555:6666:7777:8888:");
        self.ipv6test(not 1, "1111:2222::5555:6666:7777:8888:");
        self.ipv6test(not 1, "1111::5555:6666:7777:8888:");
        self.ipv6test(not 1, "::5555:6666:7777:8888:");
        self.ipv6test(not 1, "1111:2222::4444:5555:6666:7777:8888:");
        self.ipv6test(not 1, "1111::4444:5555:6666:7777:8888:");
        self.ipv6test(not 1, "::4444:5555:6666:7777:8888:");
        self.ipv6test(not 1, "1111::3333:4444:5555:6666:7777:8888:");
        self.ipv6test(not 1, "::3333:4444:5555:6666:7777:8888:");
        self.ipv6test(not 1, "::2222:3333:4444:5555:6666:7777:8888:");

        # Additional cases: http://crisp.tweakblogs.net/blog/2031/ipv6-validation-%28and-caveats%29.html
        self.ipv6test(1, "0:a:b:c:d:e:f::");
        self.ipv6test(1, "::0:a:b:c:d:e:f"); # syntactically correct, but bad form (::0:... could be combined)
        self.ipv6test(1, "a:b:c:d:e:f:0::");
        self.ipv6test(not 1, "':10.0.0.1");


if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        print '%d tests done, %d failed' % (total, fail)
