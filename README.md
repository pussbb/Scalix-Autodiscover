
The Autodiscover service minimizes user configuration and deployment steps by providing clients access to email and groupware server features.

To have fully working Autodiscover service you would need to configure your this service on main server and mail server.
Or setup DNS A record to point autodiscover.SITE.com to the server where AutoDiscover service is installed and configured.

By default order how client will try to get settings is following 
1. HTPP OPTION https://site.com/Autodiscover/Autodiscover.xml
2. HTPP POST https://site.com/Autodiscover/Autodiscover.xml
3. HTPP OPTION https://autodiscover.site.com/Autodiscover/Autodiscover.xml
4. HTPP POST https://autodiscover.site.com/Autodiscover/Autodiscover.xml
5. after all attemps can be performed  DNS SRV lookup to autodiscover.tcp.site.com that will reply to "mail.site.com"



By default all files for autodiscover service is located here 

```plain
    :~$ /opt/scalix-autodiscover/
```

CGI script is in following folder

```plain
    :~$ /opt/scalix-autodiscover/cgi
```

Config template is in following folder

```plain
    :~$ /opt/scalix-autodiscover/default
```

Dependecies
====

Centos 7 and Ubuntu/Debian higher 14.04

```plain
:~$ sudo pip install lxml ldap3
```

Ubuntu 14.04

```shell
:~$  apt install python-lxml
:~$  pip install ldap3
```

Centos 6

```shell
:~$  yum install python-lxml
:~$  pip install ldap3
```

Install
====

```shell
:~$ mkdir -p /opt/scalix-autodiscover/cgi/
:~$ mkdir -p /etc/opt/scalix-autodiscover/
:~$ cp ./autodiscover.py /opt/scalix-autodiscover/cgi/
:~$ cp ./autodiscover.ini /etc/opt/scalix-autodiscover/
```


Edit autodiscover.ini to set setup your desired values


Change permission
Centos 
```shell
:~$ chown nobody.nobody /opt/scalix-autodiscover/cgi/autodiscover.py
:~$ chown nobody.nobody /etc/opt/scalix-autodiscover/autodiscover.ini
```

Ubuntu 
```shell
:~$ chown nouser.nogroup /opt/scalix-autodiscover/cgi/autodiscover.py
:~$ chown nouser.nogroup /etc/opt/scalix-autodiscover/autodiscover.ini
```

Chmod 
```shell
:~$ chmod a+x /opt/scalix-autodiscover/cgi/autodiscover.py
:~$ chmod a+ /etc/opt/scalix-autodiscover/autodiscover.ini
```

Somewhere in config before your VirtualHost 

```plain
<Directory "/opt/scalix-autodiscover/cgi">
        AllowOverride None
        Options +ExecCGI -Includes
        AddHandler cgi-script .py
        AddHandler cgi-script .cgi
        AddHandler wsgi-script .wsgi
        <IfVersion >= 2.4>
                Require all granted
        </IfVersion>
        <IfVersion < 2.4>
                Order allow,deny
                Allow from all
        </IfVersion>
        AddDefaultCharset off
</Directory>
```

Inside VirtualHost section
```plain
    ServerAlias autodiscover.*
    Alias /autodiscover/autodiscover.xml /opt/scalix-autodiscover/cgi/autodiscover.py
    Alias /autodiscover/autodiscover.exc /opt/scalix-autodiscover/cgi/autodiscover.py
    Alias /Autodiscover/Autodiscover.xml /opt/scalix-autodiscover/cgi/autodiscover.py
    Alias /AutoDiscover/AutoDiscover.xml /opt/scalix-autodiscover/cgi/autodiscover.py
    Alias /.well-known/autoconfig/mail/config-v1.1.xml /opt/scalix-autodiscover/cgi/autodiscover.py
    Alias /mail/config-v1.1.xml /opt/scalix-autodiscover/cgi/autodiscover.py
```
