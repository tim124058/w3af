#!/bin/bash

# run as root
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"

# install dependence
apt-get update
apt-get install -y python-pybloomfiltermmap graphviz python-gtksourceview2

wget http://ftp.br.debian.org/debian/pool/main/p/pywebkitgtk/python-webkit_1.1.8-3_amd64.deb -P /tmp/dep_webkit/
wget http://ftp.br.debian.org/debian/pool/main/w/webkitgtk/libjavascriptcoregtk-1.0-0_2.4.11-3_amd64.deb -P /tmp/dep_webkit/
wget http://ftp.br.debian.org/debian/pool/main/p/python-support/python-support_1.0.15_all.deb -P /tmp/dep_webkit/
wget http://ftp.br.debian.org/debian/pool/main/w/webkitgtk/libwebkitgtk-1.0-0_2.4.11-3_amd64.deb -P /tmp/dep_webkit/
dpkg -i /tmp/dep_webkit/* || apt-get --fix-broken install -y && rm -rf /tmp/dep_webkit/

# install python dependence
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
$SCRIPTPATH/w3af_gui
/tmp/w3af_dependency_install.sh

# symbolic link
ln -s $SCRIPTPATH/w3af_* /usr/local/bin
