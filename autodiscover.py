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

"""
from __future__ import print_function

import ast
import cgi
import simplejson as json
import os
import cgitb
import sys

from ConfigParser import ConfigParser
from collections import defaultdict

import cStringIO

from datetime import datetime

from lxml import etree

from ldap3 import Server, Connection, NONE, SIMPLE, ANONYMOUS


_TREE = lambda: defaultdict(_TREE)


CONFIG_PATH = (
    os.path.realpath(os.path.dirname(__file__)),
    os.path.join(os.sep, 'etc', 'opt'),
    os.path.join(os.sep, 'etc', 'opt', 'scalix'),
    os.path.join(os.sep, 'etc', 'opt', 'scalix-autodiscover'),
)


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
            raise RuntimeError('Environment key {0} is empty'
                               ' or not found'.format(key))
        return self.from_config_file(value)

    def from_config_file(self, filename):
        """Read settings from configuration file

        :param filename: string settings filename
        :return:
        """
        if not filename:
            raise RuntimeError('File does not exists')

        filename = os.path.realpath(os.path.expanduser(filename))

        if not os.path.exists(filename):
            raise RuntimeError('File {0} does not exists'.format(filename))
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
            return protocol, DictWrapper({
                'formated': formatted,
                'raw': raw,
                'type': soc_type,
                'hostname': host,
                'port': port,
                'authentication': auth,
            })

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


class LdapClient(object):
    """Helper class to work with ldap

    """
    __LDAP_ATTR = ('cn', 'mail', 'displayName')

    def __init__(self, config):
        """

        :param config:
        """
        assert isinstance(config, Config)
        self.__config = config.get('ldap', {})
        self.__server = Server(self.__config.get('server_host'), get_info=NONE,
                               connect_timeout=80)

    def search(self, user):
        """Search for a user in ldap

        :param user: str search string
        :return: tuple (display name , email)
        """
        if not user:
            return None, None
        with self.__get_connection() as conn:
            filter_ = self.__config.get('query_filter').format(phrase=user)
            conn.search(self.__config.get('search_base'), filter_,
                        attributes=self.__LDAP_ATTR)
            if not conn.response:
                return None, None
            if len(conn.response) > 1:
                raise Exception('too many users found')
            attributes = conn.response[0].get('attributes')
            display_name = attributes.get('displayName')[0]
            emails = attributes.get('mail', [])
            for email in emails:
                if email == user:
                    return display_name, email
            else:
                return display_name, emails[0]
        return None, None

    def __get_connection(self):
        """Creates new ldap connection

        :return: Connection
        """
        kwargs = {
            'read_only': True,
            'receive_timeout': 60,
            'auto_bind': True,
            'authentication': ANONYMOUS,
            'password': self.__config.get('bind_pw'),
            'user': self.__config.get('bind_dn')
        }
        if kwargs['password'] or kwargs['user']:
            kwargs['authentication'] = SIMPLE
        return Connection(self.__server, **kwargs)


class AutoDiscoverView(object):
    """Generic class for Autodiscover document generators

    """

    _content_type = 'text/xml; charset=utf-8'

    def __init__(self, config):
        self._config = config
        self._user_display_name = None
        self._user_email = None
        self.__stream = self._config.get('stream', cStringIO.StringIO())
        self.__headers = []

    def __getattr__(self, item):
        if item in self._config:
            return self._config[item]
        return self._config.general[item]

    def _add_header(self, header):
        self.__headers.append(header)

    def send(self):
        """Prints autodiscover document for HTTP request

        :return:
        """
        for header in self.__headers:
            self.output(header + "\r\n")
        if self._content_type:
            self.output("Content-Type: {0}\n".format(self._content_type))
        self.output("\n")
        self._process()
        self.output("\n")

    def build(self):
        """Build autodiscover document

        :return: str
        """
        return str(self)

    def _process(self):
        """Abstract method  for sub classes which must print xml document
        for specific format

        :return:
        """
        raise NotImplementedError

    def output(self, msg):
        """Prints string to stream

        :param msg: str
        :return:
        """
        self.__stream.write(msg)

    def __str__(self):
        old_stream = self.__stream
        self.__stream = cStringIO.StringIO()
        self._process()
        try:
            return self.__stream.getvalue()
        finally:
            self.__stream = old_stream

    def set_user_info(self, display_name, email):
        """Set user info

        :param display_name: str
        :param email: str
        :return:
        """
        self._user_display_name = display_name
        self._user_email = email

    @property
    def user_email(self):
        """Users email address

        :return:
        """
        return self._user_email

    @property
    def user_display_name(self):
        """User display name

        :return: any
        """
        return self._user_display_name


class ConfigV1(AutoDiscoverView):
    """Autodiscover document generator for config.v.1.xml (ThunderBird, Kmail )

    """

    def _process(self):
        """Generate config.v.1.xml

        :return:
        """
        self.output('<clientConfig version="1.1">')
        self.output('<emailProvider id="{0}">'.format(self.provider))

        self.output('<domain>{0}</domain>'.format(self.hostname))
        self.output('<displayName>{0}</displayName>'.format(self.name))
        self.output('<displayShortName>{0}</displayShortName>'.format(
            self.short_name
        ))

        self.__proccess_protocol('incomingServer', ['imap', 'pop3'])
        self.__proccess_protocol('outgoingServer', ['smtp'])

        for doc in self._config.documentation.values():
            self.output('<documentation url="{0}">'.format(doc.pop('link')))
            for lang, descr in doc.items():
                self.output('<descr lang="{0}">{1}</descr>'.format(lang, descr))
            self.output('</documentation>')

        self.output('</emailProvider></clientConfig>')

    def __proccess_protocol(self, tag_name, items):
        """Generate xml section for specified protocols

        :param tag_name: string xml tag name
        :param items: list of allowed protocols
        :return:
        """
        for protocol, settings in self._config.protocols:
            for item in items:
                if protocol.startswith(item):
                    self.output('<{0} type="{1}">'.format(tag_name, item))
                    self.__process_protocol_settings(settings)
                    self.output('</{0}>'.format(tag_name))

    def __process_protocol_settings(self, settings):
        """Generates xml for protocol connection details

        :param settings: dict
        :return:
        """
        self.output('<hostname>{0}</hostname>'.format(settings.hostname))
        self.output('<port>{0}</port>'.format(settings.port))
        self.output('<socketType>{0}</socketType>'.format(settings.type))
        self.output('<authentication>{0}</authentication>'.format(
            settings.authentication
        ))
        user_name = '%EMAILADDRESS%'
        if self.user_email:
            user_name = self.user_email
        self.output('<username>{0}</username>'.format(user_name))


class MicrosoftAutodiscover(AutoDiscoverView):
    """Microsoft Autodiscover document generator

    """

    def __init__(self, config, xml):
        super(MicrosoftAutodiscover, self).__init__(config)
        self._responses = []

        if xml:
            self.__parse_xml_doc(xml)

    def __parse_xml_doc(self, xml):
        """parse Autodiscover xml document

        :param xml:
        :return:
        """
        if not isinstance(xml, str):
            xml = xml.encode()
        xml = etree.fromstring(xml).getchildren()[0]

        for element in xml.iter():
            if 'EMailAddress' in element.tag:
                self._user_email = element.text
            if 'AcceptableResponseSchema' in element.tag:
                self._responses.append(element.text)

    def send(self):
        """

        :return:
        """
        if os.environ['REQUEST_METHOD'] == 'OPTIONS':
            self.output("Status: 451 ActiveSync is there\n")
            self.output("X-MS-Location: {0}\n".format(self.active_sync_host))
            self.output("Cache-Control: private\n")
            self.output("Content-Length: 0\n")
            self.output("\n")
        else:
            super(MicrosoftAutodiscover, self).send()

    def _process(self):
        """

        :return:
        """
        self.output("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        self.output('<Autodiscover xmlns="http://schemas.microsoft.com/'
                    'exchange/autodiscover/responseschema/2006">')

        if not self._responses:
            self.__error('', )
            return

        if not self._responses:
            self.__error('', )

        for response in self._responses:
            if 'mobilesync' in response:
                self.__mobile_sync()
            elif 'outlook' in response:
                self.__outlook_sync()
            else:
                self.__error(response)

        self.output('</Autodiscover>')

    def __error(self, response):
        """

        :return:
        """
        self.output('<Response xmlns="{0}">'.format(response))
        self.output('<Error Time="{0}" Id="{1}">'.format(
            datetime.now().strftime('%H:%M:%S.%f'),
            2477272013
        ))
        self.output('<ErrorCode>600</ErrorCode>')
        self.output('<Message>Invald request</Message>')
        self.output('<DebugData/>')
        self.output('</Error>')
        self.output('</Response>')

    def __mobile_sync(self):
        """Prints Autodiscover response document for Activesync

        :return:
        """
        self.output('<Response xmlns="http://schemas.microsoft.com/'
                    'exchange/autodiscover/mobilesync/responseschema/2006">')
        self.output('<Culture>en:us</Culture>')
        self.output('<User>')
        self.output('<DisplayName>{0}</DisplayName>'.format(
            self.user_display_name
        ))
        self.output('<EMailAddress>{0}</EMailAddress>'.format(self.user_email))
        self.output('</User>')

        self.output('<Action>')

        self.output('<Settings>')
        self.output('<Server>')
        self.output('<Type>MobileSync</Type>')

        self.output('<Url>{0}</Url>'.format(self.active_sync_host))
        self.output('<Name>{0}</Name>'.format(self.name))
        self.output('</Server>')
        self.output('</Settings>')

        self.output('</Action>')
        self.output('</Response>')

    def __outlook_sync(self):
        """Prints Autodiscover response document

        :return:
        """
        self.output('<Response xmlns="http://schemas.microsoft.com/exchange/'
                    'autodiscover/outlook/responseschema/2006a">')

        self.output('<User>')
        self.output('<DisplayName>{0}</DisplayName>'.format(
            self.user_display_name
        ))
        self.output('<EMailAddress>{0}</EMailAddress>'.format(self.user_email))
        self.output('</User>')
        self.output('<Account>')
        self.output('<AccountType>email</AccountType>')
        self.output('<Action>settings</Action>')
        self.output('<ServiceHome>{0}</ServiceHome>'.format(self.provider))

        protocols = dict(self._config.protocols)
        for item in ['imap', 'pop3', 'smtp']:
            settings = protocols.get(item + 's', protocols.get(item))
            if settings:
                self.output('<Protocol>')
                self.output('<Type>{0}</Type>'.format(item))
                self.output('<Server>{0}</Server>'.format(settings.hostname))
                self.output('<Port>{0}</Port>'.format(settings.port))
                self.output('<LoginName>{0}</LoginName>'.format(
                    self.user_email
                ))
                self.output('<SPA>off</SPA>')
                self.output('<SSL>{0}</SSL>'.format(settings.type))
                self.output('<AuthRequired>on</AuthRequired>')
                self.output('</Protocol>')

        self.output('</Account>')
        self.output('</Response>')


class WellKnownAutodiscover(AutoDiscoverView):

    def __init__(self, request_uri, config):
        super(WellKnownAutodiscover, self).__init__(config)
        self._request_uri = request_uri

    def send(self):
        """Process request

        :return: void
        """
        if not self._request_uri:
            self.output("Status: 400 Bad request\r\n")

        if 'host-meta' in self._request_uri:
            self._content_type = 'application/xml; charset=utf-8'
            if ('json' in os.environ.get('ACCEPT', '')
                    or '.json' in self._request_uri):
                self._content_type = 'application/json; charset=utf-8'
            super(WellKnownAutodiscover, self).send()
            return

        parts = filter(None, self._request_uri.split('/'))[1:]
        well_known = self._config.get('well-known', {})

        for part in parts:
            url = well_known.get(part)
            if url:
                self.output("Status: 301 Moved Permanently\r\n")
                self.output('Location: ' + url + "\r\n")
                self.output("\r\n")
                return
        else:
            self.output("Status: 404 Not Found\r\n")

    def __get_host_meta_links(self):
        host_meta = self._config.get('host-meta', {})
        for item in host_meta.values():
            item = ast.literal_eval(item)
            rel = item[0]
            url = item[1]
            descr = ''
            if len(item) == 3:
                descr = item[2]
            yield rel, url, descr

    def _process(self):
        """Process request

        :return: void
        """
        if 'json' in self._content_type:
            res = []
            for link in self.__get_host_meta_links():
                rel, url, descr = link
                res.append({
                    'link': rel,
                    'url': url,
                    'titles': {
                        'default': descr
                    }
                })
            self.output(json.dumps({'links': res}))
            return

        self.output("<?xml version='1.0' encoding='utf-8'?>")
        self.output('<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">')
        for link in self.__get_host_meta_links():
            rel, url, descr = link
            self.output('<Link rel="{0}" href="{1}">'.format(rel, url))
            if descr:
                self.output("<Title>{0}</Title>".format(descr))
            self.output('</Link>')
        self.output('</XRD>')


def guess_config_filenames(domain):
    """Generates a list with possible domain names.

    Example:
    >>> guess_config_filenames('scalix.com')
    ['scalix.com']
    >>> guess_config_filenames('rpm.scalix.com')
    ['rpm.scalix.com', 'scalix.com']
    >>> guess_config_filenames('192.1.3.3.3')
    ['192.1.3.3.3', '1.3.3.3', '3.3.3', '3.3']
    >>> guess_config_filenames('com')
    ['com']
    >>> guess_config_filenames('.')
    []
    >>> guess_config_filenames(None)
    []


    :param domain: string
    :return: list of possible domain names
    """
    if not domain:
        return []

    parts = filter(None, domain.split('.'))

    if len(parts) == 1:
        return parts

    res = []
    tld_index = len(parts) - 2
    for index, _ in enumerate(parts):
        if tld_index == index:
            res.append('.'.join(parts[index:]))
            break
        res.append('.'.join(parts[index:]))
    return res


def find_config(hostname):
    """Tries to find config file for specified domain

    :param hostname: string
    :return: str or None
    """
    domains = guess_config_filenames(hostname) + ['']
    for domain in domains:
        if domain:
            domain = '{0}{1}'.format(domain, '.')
        for path in CONFIG_PATH:
            cfg_file = '{0}{1}{2}autodiscover.ini'.format(path, os.sep, domain)
            if os.path.exists(cfg_file):
                return cfg_file
    return None


def main():
    """

    :return:
    """
    if 'SERVER_PROTOCOL' in os.environ:
        cgitb.enable()

    request = cgi.FieldStorage()
    config = Config(stream=sys.stdout)
    config.from_config_file(find_config(os.environ.get('HTTP_HOST')))

    view = None
    ldap = LdapClient(config)
    try:
        email_addr = request.getfirst('emailaddress')
    except TypeError as _:
        traceback.print_exc()
        email_addr = None

    request_uri = os.environ.get('REQUEST_URI', '')

    if '.well-known' in request_uri and 'mail/config' not in request_uri:
        view = WellKnownAutodiscover(request_uri, config)
    elif email_addr:
        view = ConfigV1(config)
        view.set_user_info(*ldap.search(email_addr))
    else:
        xml = ''
        if isinstance(request.value, list):
            for field in request.value:
                xml = ''.join([xml, '='.join([field.name, field.value])])
        else:
            xml = request.value

        view = MicrosoftAutodiscover(config, xml)
        view.set_user_info(*ldap.search(view.user_email))

    if 'SERVER_PROTOCOL' in os.environ:
        view.send()
    else:
        print(view.build())


if __name__ == '__main__':
    import traceback
    try:
         main()
    except:
        print("\n\n<PRE>")
        traceback.print_exc()
