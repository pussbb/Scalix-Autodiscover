
The Autodiscover service minimizes user configuration and deployment steps by providing clients access to email and groupware server features.

To have fully working Autodiscover service you would need to configure your this service on main server and mail server.
Or setup DNS A record to point autodiscover.SITE.com to the server where AutoDiscover service is installed and configured.

By default order how client will try to get settings is following 
1. HTPP OPTION https://site.com/Autodiscover/Autodiscover.xml
2. HTPP POST https://site.com/Autodiscover/Autodiscover.xml
3. HTPP OPTION https://autodiscover.site.com/Autodiscover/Autodiscover.xml
4. HTPP POST https://autodiscover.site.com/Autodiscover/Autodiscover.xml
5. after all attemps can be performed  DNS SRV lookup to autodiscover.tcp.site.com that will reply to "mail.site.com"


[Manual-Installation](../../wiki/Manual-Installation)

[Installing-with-system-package-manager](../../wiki/Installing-with-system-package-manager)
