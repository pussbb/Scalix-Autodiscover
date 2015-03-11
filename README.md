# Scalix-Autodiscover
On Apache configuration file VirtualHost section add lines like:
```plain
   Alias /autodiscover/autodiscover.xml /path/to/autodiscover/Scalix-Autodiscover.py
   Alias /Autodiscover/Autodiscover.xml /path/to/autodiscover/Scalix-Autodiscover.py
   Alias /AutoDiscover/AutoDiscover.xml /path/to/autodiscover/Scalix-Autodiscover.py
   Alias  /.well-known/autoconfig/mail/config-v1.1.xml /path/to/autodiscover/Scalix-Autodiscover.py
   Alias /mail/config-v1.1.xml /path/to/autodiscover/Scalix-Autodiscover.py
```

Check syntax
```sh
apachectl -t
```
than you can restart or reload apache server.
```sh
service httpd restart 
```
```sh
service httpd reload
```

On Scalix-Autodiscover.py add your mail domain and server FQDN where located all or separate Scalix services, 
for e.g.:
```plain
MAIL_DOMAIN = 'example.com'
DOMAIN = MAIL_DOMAIN
HOSTNAME['imap'] = 'sximap.' + DOMAIN
HOSTNAME['pop3'] = 'sxpop3.' + DOMAIN
HOSTNAME['smtp'] = 'sxsmtp.' + DOMAIN
MS_CONFIG['MobileSync'] = "https://sxAS." + DOMAIN + ":443/Microsoft-Server-ActiveSync"
```
In this case you have:
SMTP server: sxsmtp.example.com
IMAP server: sximap.example.com
POP3 server: sxpop3.example.com
ActiveSync server: "https://sxAS.example.com:443/Microsoft-Server-ActiveSync"
