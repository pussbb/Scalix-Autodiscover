#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 Scalix, Inc. (www.scalix.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Street #330, Boston, MA 02111-1307, USA.
#

import os
import cgi
import cgitb
from datetime import datetime
from cgi import parse_qs
from xml.dom.minidom import parseString
cgitb.enable()

user_agent = os.environ


# *** CONFIGURATION ***
MAIL_DOMAIN = 'example.com'

DOMAIN = MAIL_DOMAIN
HOSTNAME = {'imap': 'imap.' + DOMAIN,
            'pop3': 'pop.' + DOMAIN,
            'smtp': 'smtp.' + DOMAIN}

MS_CONFIG = {'MobileSync': "https://activesync." + DOMAIN + ":443/Microsoft-Server-ActiveSync",
             'IMAP': {'Server': HOSTNAME['imap'],
                      'Port': "993",
                      'SSL': "on",
                      'SPA': "off",
                      'AuthRequired': "on"},
             'SMTP': {'Server': HOSTNAME['smtp'],
                      'Port': "25",
                      'SSL': "on",
                      'SPA': "off",
                      'AuthRequired': "on"
             }}
# ActiveSync URL.

# IMAP configuration settings.

# SMTP configuration settings.
# *** End Configuration ***


class MozillaThunderbird(object):
    """ Mozilla Thunderbird autodiscover class.
    /*
    <socketType>SSL</socketType>
        <!-- "plain": no encryption
        "SSL": SSL 3 or TLS 1 on SSL-specific port
        "STARTTLS": on normal plain port and mandatory upgrade to TLS via STARTTLS 
        -->
    
    <authentication>password-cleartext</authentication>
        "plain" (deprecated): Send password in the clear (dangerous, if SSL isn't used either).AUTH PLAIN, LOGIN
        or protocol-native login.
        "password-encrypted",
        "secure" (deprecated): A secure encrypted password mechanism.Can be CRAM-MD5 or DIGEST-MD5. Not NTLM.
        "NTLM": Use NTLM (or NTLMv2 or successors),the Windows login mechanism.
        "GSSAPI": Use Kerberos / GSSAPI,a single-signon mechanism used for big sites.
        "client-IP-address": The server recognizes this user based on the IP address. No authentication needed, \
        the server will require no username nor password.
        "TLS-client-cert": On the SSL/TLS layer, the server requests a client certificate and the client sends
        one (possibly after letting the user select/confirm one),
        if available. (Not yet supported by Thunderbird)
        "none": No authentication

    Compatibility note: Thunderbird 3.0 accepts only "plain" and "secure". It will ignore the whole XML file, if other
     values are given. -->
    */    
    
    
    <clientConfig version="1.1">
        <emailProvider id="[$MAIL_DOMAIN]">
            <domain>[$DOMAIN]</domain>
            <displayName>[$DOMAIN] Mail</displayName>
            <displayShortName>[$DOMAIN]</displayShortName>
                ......
                <incomingServer type="[$protocol]">
                    <hostname>[$[$protocol]_server]</hostname>
                    <port>Port</port>
                    <socketType>[$socketType]</socketType>
                    <authentication>[$auth_method]</authentication>
                    <username>%EMAILADDRESS%</username>
                </incomingServer>
                ......
                
        </emailProvider>
    </clientConfig>
    """

    def __init__(self, _protocols):
        self.protocols = _protocols

    @staticmethod
    def get_protolols_config():
        """ protocols(
                    'imap/tls',
                    'imaps',
                    'pop3/tls',
                    'pop3s',
                    'smtps',
                    'smtp/tls-587',
                    'smtp/tls',
                    'smtp',
                    'pop3',
                    'imap',
                    );
        """
        ret_dict = {}

        tmp_dict = {'protocol': 'imap', 'host': HOSTNAME['imap'], 'port': '143', 'socketType': 'plain',
                    'authentication': 'plain'}
        # imap,pop3,smtp
        ret_dict['imap'] = tmp_dict

        tmp_dict = {'protocol': 'pop3',
                    'host': HOSTNAME['pop3'],
                    'port': '110',
                    'socketType': 'plain',
                    'authentication': 'plain'
        }
        ret_dict['pop3'] = tmp_dict

        tmp_dict = {'protocol': 'smtp',
                    'host': HOSTNAME['smtp'],
                    'port': '25',
                    'socketType': 'plain',
                    'authentication': 'plain'
        }
        ret_dict['smtp'] = tmp_dict

        # imap/tls, pop3/tls, smtp/tls
        tmp_dict = {'protocol': 'imap',
                    'host': HOSTNAME['imap'],
                    'port': '143',
                    'socketType': 'STARTTLS',
                    'authentication': 'plain'
        }
        ret_dict['imap/tls'] = tmp_dict

        tmp_dict = {'protocol': 'pop3',
                    'host': HOSTNAME['pop3'],
                    'port': '110',
                    'socketType': 'STARTTLS',
                    'authentication': 'plain'
        }
        ret_dict['pop3/tls'] = tmp_dict

        tmp_dict = {'protocol': 'smtp',
                    'host': HOSTNAME['smtp'],
                    'port': '25',
                    'socketType': 'STARTTLS',
                    'authentication': 'plain'
        }
        ret_dict['smtp/tls'] = tmp_dict

        tmp_dict = {'protocol': 'smtp',
                    'host': HOSTNAME['smtp'],
                    'port': '587',
                    'socketType': 'STARTTLS',
                    'authentication': 'plain'
        }
        ret_dict['smtp/tls-587'] = tmp_dict

        # imaps,pop3s,smtps
        tmp_dict = {'protocol': 'imap',
                    'host': HOSTNAME['imap'],
                    'port': '993',
                    'socketType': 'SSL',
                    'authentication': 'plain'
        }
        ret_dict['imaps'] = tmp_dict

        tmp_dict = {'protocol': 'pop3',
                    'host': HOSTNAME['pop3'],
                    'port': '995',
                    'socketType': 'SSL',
                    'authentication': 'plain'
        }
        ret_dict['pop3s'] = tmp_dict

        tmp_dict = {'protocol': 'smtp',
                    'host': HOSTNAME['smtp'],
                    'port': '465',
                    'socketType': 'SSL',
                    'authentication': 'plain'
        }
        ret_dict['smtps'] = tmp_dict
        # for a in ret_dict.keys():
        # print(ret_dict[a])

        return ret_dict

    def get_xml(self):
        prot_conf = self.get_protolols_config()
        ret = """<clientConfig version="1.1"> 
                   <emailProvider id="%s">
                       <domain>%s</domain>
                       <displayName>%s Mail</displayName>
                       <displayShortName>%s</displayShortName>
              """ % (MAIL_DOMAIN, MAIL_DOMAIN, DOMAIN, DOMAIN)

        for protocol in self.protocols:
            if protocol.count('smtp'):
                ret += """ <outgoingServer type="%s">
                               <hostname>%s</hostname>
                               <port>%s</port>
                               <socketType>%s</socketType>
                               <authentication>%s</authentication>
                       """ % (prot_conf[protocol]['protocol'],
                              prot_conf[protocol]['host'],
                              prot_conf[protocol]['port'],
                              prot_conf[protocol]['socketType'],
                              prot_conf[protocol]['authentication']
                )
                ret += "<username>%EMAILADDRESS%</username>"
                ret += "</outgoingServer>"
            else:
                ret += """ <incomingServer type="%s">
                               <hostname>%s</hostname>
                               <port>%s</port>
                               <socketType>%s</socketType>
                               <authentication>%s</authentication>
                       """ % (prot_conf[protocol]['protocol'],
                              prot_conf[protocol]['host'],
                              prot_conf[protocol]['port'],
                              prot_conf[protocol]['socketType'],
                              prot_conf[protocol]['authentication']
                )
                ret += "<username>%EMAILADDRESS%</username>"
                ret += "</incomingServer>"
        ret += "</emailProvider></clientConfig>"
        return ret


class MicrosoftAutodiscover(object):
    """
    <?xml version="1.0" encoding="utf-8"?>
    <Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/mobilesync/requestschema/2006">
         <Request>
             <EMailAddress>chris@woodgrovebank.com</EMailAddress>
             <AcceptableResponseSchema>
                 http://schemas.microsoft.com/exchange/autodiscover/mobilesync/
                 responseschema/2006
             </AcceptableResponseSchema>
         </Request>
    </Autodiscover>
    
    Successful response
    
    <?xml version="1.0" encoding="utf-8"?>
    <Autodiscover xmlns:autodiscover="http://schemas.microsoft.com/exchange/autodiscover/mobilesync/responseschema/2006">
        <autodiscover:Response>
            <autodiscover:Culture>en:us</autodiscover:Culture>
            <autodiscover:User>
               <autodiscover:DisplayName>Chris Gray</autodiscover:DisplayName>
               <autodiscover:EMailAddress>chris@woodgrovebank.com</autodiscover:EMailAddress>
            </autodiscover:User>
            <autodiscover:Action>
                <autodiscover:Settings>
                    <autodiscover:Server>
                       <autodiscover:Type>MobileSync</autodiscover:Type>
                       <autodiscover:Url>https://loandept.woodgrovebank.com/Microsoft-Server-ActiveSync</autodiscover:Url>
                       <autodiscover:Name>https://loandept.woodgrovebank.com/Microsoft-Server-ActiveSync</autodiscover:Name>
                    </autodiscover:Server>
                    <autodiscover:Server>
                        <autodiscover:Type>CertEnroll</autodiscover:Type>
                        <autodiscover:Url>https://cert.woodgrovebank.com/CertEnroll</autodiscover:Url>
                        <autodiscover:Name />
                        <autodiscover:ServerData>CertEnrollTemplate</autodiscover:ServerData>
                    </autodiscover:Server>
                </autodiscover:Settings>
            </autodiscover:Action>
         </autodiscover:Response>
     </Autodiscover>


    Error responses

    <?xml version="1.0" encoding="utf-8"?>
    <Autodiscover xmlns:autodiscover="http://schemas.microsoft.com/exchange/autodiscover/mobilesync/responseschema/2006">
      <autodiscover:Response>
         <autodiscover:Error Time="16:56:32.6164027" Id="1054084152">
             <autodiscover:ErrorCode>600</autodiscover:ErrorCode>
             <autodiscover:Message>Invalid Request</autodiscover:Message>
             <autodiscover:DebugData />
        </autodiscover:Error>
      </autodiscover:Response>
    </Autodiscover>
    """

    def __init__(self, request):
        dom = parseString(request)
        data = dom.getElementsByTagName('AcceptableResponseSchema')
        self.schema = data[0].firstChild.nodeValue
        data = dom.getElementsByTagName('EMailAddress')
        self.email = data[0].firstChild.nodeValue

    def outlook(self):
        ret = """<Autodiscover xmlns='http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006'>"
                     <Response xmlns='%s'>
                         <Account>
                         <AccountType>email</AccountType>
                         <Action>settings</Action>
              """ % self.schema
        # Loop through each configured protocol.
        for protocol in MS_CONFIG.keys():
            if protocol == 'MobileSync':
                continue
            ret += "<Protocol><Type>%s</Type>" % protocol
            for key, value in MS_CONFIG[protocol].items():
                ret += "\t\t\t\t\t\t\t<%s>%s</%s>\n" % (key, value, key)
            ret += "</Protocol>"
        ret += """</Account>
                </Response>
            </Autodiscover>
            """
        return ret

    def mabilesync(self):
        """
        correct answer from https://testconnectivity.microsoft.com
        <?xml version="1.0"?>
        <Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >
        <Response xmlns="http://schemas.microsoft.com/exchange/autodiscover/mobilesync/responseschema/2006">
        <Culture>en:us</Culture>
        <User>
        <DisplayName>vth</DisplayName>
        <EMailAddress>vth@sxex.cmhtransfer.com</EMailAddress>
        </User>
        <Action>
        <Settings>
        <Server>
        <Type>MobileSync</Type>
        <Url>https://sxex.cmhtransfer.com/Microsoft-Server-ActiveSync</Url>
        <Name>https://sxex.cmhtransfer.com/Microsoft-Server-ActiveSync</Name>
        </Server>
        </Settings>
        </Action>
        </Response>
        </Autodiscover>
        """
        ret = """<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >
                      <Response xmlns="%s">
                          <Culture>en:en</Culture>
                  <User>
                      <DisplayName>%s</DisplayName>
                      <EMailAddress>%s</EMailAddress>
                  </User>
                      <Action>
                              <Settings>
                          <Server>
                              <Type>MobileSync</Type>
                          <Url>%s</Url>
                          <Name>%s</Name>
                                  </Server>
                          </Settings>
                          </Action>
             </Response>
                  </Autodiscover>
            """ % (self.schema, self.email.split('@')[0], self.email, MS_CONFIG['MobileSync'], MS_CONFIG['MobileSync'])

        # return ''.join(ret.split())

        return ret

    @staticmethod
    def ms_unknown():

        d = datetime.now()
        # d.strftime('%H:%M:%S.%f')
        ret = """ <Autodiscover xmlns=\"http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006\">
                      <Response>
                          <Error Time='%s' Id='%s'>
                              <ErrorCode>600</ErrorCode>
                              <Message>Invalid Request</Message>
                              <DebugData/>
                          </Error>
                     </Response> 
                  </Autodiscover>
           """ % (d.strftime('%H:%M:%S.%f'), '2477272013')
        return ret

    def get_xml(self):
        if self.schema.count('/mobilesync/'):
            return self.mabilesync()
        elif self.schema.count('/outlook/'):
            return self.outlook()
        else:
            return self.ms_unknown()


print "Content-Type: text/xml; charset=utf-8"
print('')

GET_dict = {}
form = cgi.FieldStorage()     

# Method GET --Mozilla Thunderbird
try:
    GET_dict = parse_qs(os.environ.get('QUERY_STRING'))
except Exception:
    pass

if 'emailaddress' in GET_dict.keys():
        protocols = ('imaps',
                     'pop3s',
                     'smtps',
        )
        mthb = MozillaThunderbird(protocols)
        print("<?xml version='1.0' encoding='UTF-8'?>")
        print(mthb.get_xml())
        exit(0)

try:
    # Method POST --ActiveSync, Outlook
    POST_str = str(form.value)

    if len(POST_str) > 100:
        msad = MicrosoftAutodiscover(POST_str)
        # print("<?xml version='1.0' encoding='UTF-8'?>")
        print("""<?xml version="1.0"?>""")
        print(msad.get_xml())
except Exception:
    pass

exit(0)
