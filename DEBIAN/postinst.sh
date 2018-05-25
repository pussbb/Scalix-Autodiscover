#!/bin/bash
apache2_base="/etc/apache2/"
apache2_mods_av="$apache2_base/mods-available"
apache2_mods_en="$apache2_base/mods-enabled"

$(type -p pip) install -r /opt/scalix-autodiscover/requirements.txt

function enable_apache_mods() {
  for ext in "conf" "load"
  do
    file="$1.$ext"
    if [ -f "$apache2_mods_av/$file" -a ! -f  "$apache2_mods_en/$file" ]; then
      ln -s "$apache2_mods_av/$file" "$apache2_mods_en/$file"
    fi
  done
}

mods="cgi"
a2enmod_cmd=$(type -P a2enmod)

for mod in $mods
do
    if [ -z "$a2enmod_cmd" ]; then
        enable_apache_mods $mod
    else
        $a2enmod_cmd $mod
    fi
done

chown nouser.nogroup /opt/scalix-autodiscover/cgi/autodiscover.py
chown nouser.nogroup /etc/opt/scalix-autodiscover/autodiscover.ini
chmod a+x /opt/scalix-autodiscover/cgi/autodiscover.py
chmod a+ /etc/opt/scalix-autodiscover/autodiscover.ini