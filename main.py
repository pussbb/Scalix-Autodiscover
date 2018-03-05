#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright 2014 Scalix, Inc. (www.scalix.com)

This program is free software; you can redistribute it and/or
modify it under the terms of version 2 of the GNU General Public
License as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Street #330, Boston, MA 02111-1307, USA.


# run python -m CGIHTTPServer

"""

from autodiscover import Config, LdapClient, CONFIG_PATH

if __name__ == '__main__':
    config = Config()
    config.from_config_file('./autodiscover.ini')
    print(CONFIG_PATH)
    for protocol, settings in config.protocols:
        print(protocol, settings)
    print(config.documentation['wiki'])
    print(config.general)
    ldap = LdapClient(config)
    print(ldap.search('vando.ribeiro'))
    print(ldap.search('vando.ribeiro@2mi.com.br'))
