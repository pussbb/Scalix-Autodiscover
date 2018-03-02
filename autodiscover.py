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

"""


import os
from ConfigParser import ConfigParser
from collections import defaultdict


_TREE = lambda: defaultdict(_TREE)


class DictWrapper(dict):
    """Helper wrapper for a dict with a few helper things

    """

    def __getattr__(self, item):
        return self[item]


class Default(DictWrapper):
    """Generic class to ignore missing elements

    """

    def __getitem__(self, item):
        if item not in self:
            return ''
        return super(Default, self).__getitem__(item)

    def __missing__(self, key):
        return key


class Config(DictWrapper):
    """Base class to read configuration

    """

    def from_envvar(self, key):
        """Read filename path from environment variable

        :param key: string name of environment variable
        :return: self
        """
        value = os.environ.get(key)
        if not value:
            raise RuntimeError('Environment key {} is empty'
                               ' or not found'.format(key))
        return self.from_config_file(value)

    def from_config_file(self, filename):
        """Read settings from configuration file

        :param filename: string settings filename
        :return:
        """
        filename = os.path.realpath(os.path.expanduser(filename))
        if not os.path.exists(filename):
            raise RuntimeError('File {} does not exists'.format(filename))
        config_parser = ConfigParser(allow_no_value=True)
        config_parser.read(filename)
        for section in config_parser.sections():
            self[section] = dict(list(self.get(section, {}))
                                 + config_parser.items(section))
        return self

    @property
    def authentication_methods(self):
        """Get settings for authentication method

        :return: dict
        """
        return self.get('authentication', {'default': 'password-cleartext'})

    @property
    def protocols(self):
        """List of enabled protocols for Autodiscover service

        :return: dict
        """
        template_data = Default(**self.get('general', {}))
        auth_method = self.get('authentication',
                               {'default': 'password-cleartext'})

        def __repr_entry(protocol, raw):
            """Parse url from config file to more readable.

            :param protocol: string protocol name
            :param raw: string
            :return: dict
            """
            formatted = raw.format(template_data)
            soc_type, host, port = [item.strip(' /')
                                    for item in formatted.split(':')]
            auth = auth_method.get(protocol, auth_method.get('default'))
            return protocol, {
                'formated': formatted,
                'raw': raw,
                'type': soc_type,
                'hostname': host,
                'port': port,
                'authentication': auth,
            }

        for name, value in self.get('protocols', {}).items():
            yield __repr_entry(name, value)

    @property
    def documentation(self):
        """List of external links for Autodiscover service.

        :return: dict
        """

        result = _TREE()
        for key, value in self.get('documentation', {}).items():
            if '_' in key:
                key, lang = key.split('_', 1)
                result[key][lang] = value
            else:
                result[key]['link'] = value
        return result
