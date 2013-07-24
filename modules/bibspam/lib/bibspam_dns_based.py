# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" Library to check if a URL is spam based on DNS blacklists.
    e.g. http://spamhaus.org/ """

__revision__ = "$Id$"

import socket
from urlparse import urlparse

def is_valid_ipv4_address(address):
    """ Validate IPv4 address
        http://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python """
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError: # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error: # not a valid address
        return False
    return True


class SpamDnsBase():
    """ To check an ip against a DNS based spam detection service,
        a) get the ip and reverse it 1.2.3.4  -> 4.3.2.1
        b) an example host is zen.spamhaus.org
        c) do the lookup 4.3.2.1.zen.spamhaus.org
        d) if there is a result, the ip is a spam host else
            there is an exception and it is not in the spam list
            of this spam detection host."""

    def __init__(self, host):
        """ host can be one of three services
            http://www.spamhaus.org/, SURBL or URIBL,
            setting is imported from etc/bibspam/bibspam.cfg """
        self.host = host.strip()

    def is_spam(self, item):
        """ Check if item is spam, return True if it yes """
        if not is_valid_ipv4_address(item):
            url_parts = urlparse(item)
            ip = socket.gethostbyname(url_parts.netloc)
        else:
            ip = item
        ip = ip.split('.')
        ip.reverse()
        ip_to_check = ".".join(ip) + "." + self.host
        try:
            socket.gethostbyname(ip_to_check)
            return True
        except:
            return False
