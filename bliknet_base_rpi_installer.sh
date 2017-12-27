#!/usr/bin/env bash
# Based on: Home Assistant Raspberry Pi Installer Kickstarter
# Copyright (C) 2017 Geurt Lagemaat - All Rights Reserved
# Permission to copy and modify is granted under the MIT License
# Last revised 12/27/2017

## Run pre-install apt package dependency checks ##

while getopts ":n" opt; do
  case $opt in
    n)

    me=$(whoami)
    
    sudo apt-get update
    
    PKG_PYDEV=$(dpkg-query -W --showformat='${Status}\n' python-dev|grep "install ok installed")
    echo Checking for python-dev: $PKG_PYDEV
    if [ "" == "$PKG_PYDEV" ]; then
      echo "No python-dev. Setting up python-dev."
      sudo apt-get --force-yes --yes install python-dev
    fi

    PKG_PYPIP=$(dpkg-query -W --showformat='${Status}\n' python-pip|grep "install ok installed")
    echo Checking for python-pip: $PKG_PYPIP
    if [ "" == "$PKG_PYPIP" ]; then
      echo "No python-pip. Setting up python-pip."
      sudo apt-get --force-yes --yes install python-pip
    fi

    PKG_GIT=$(dpkg-query -W --showformat='${Status}\n' git|grep "install ok installed")
    echo Checking for git: $PKG_GIT
    if [ "" == "$PKG_GIT" ]; then
      echo "No git. Setting up git."
      sudo apt-get --force-yes --yes install git
    fi
    
    PKG_LIBSSL_DEV=$(dpkg-query -W --showformat='${Status}\n' libssl-dev|grep "install ok installed")
    echo Checking for libssl-dev: $PKG_LIBSSL_DEV
    if [ "" == "$PKG_LIBSSL_DEV" ]; then
      echo "No libssl-dev. Setting up libssl-dev."
      sudo apt-get --force-yes --yes install libssl-dev
    fi
	
	PKG_BLUETOOTH=$(dpkg-query -W --showformat='${Status}\n' bluetooth|grep "install ok installed")
    echo Checking for bluetooth: $PKG_BLUETOOTH
    if [ "" == "$PKG_BLUETOOTH" ]; then
      echo "No bluetooth. Setting up bluetooth."
      sudo apt-get --force-yes --yes install bluetooth
    fi
	
	PKG_LIBBLUETOOTH=$(dpkg-query -W --showformat='${Status}\n' libbluetooth-dev|grep "install ok installed")
    echo Checking for bluetooth: $PKG_LIBBLUETOOTH
    if [ "" == "$PKG_LIBBLUETOOTH" ]; then
      echo "No libbluetooth-dev. Setting up libbluetooth-dev."
      sudo apt-get --force-yes --yes install libbluetooth-dev
    fi
	
	PKG_LIBBOOST=$(dpkg-query -W --showformat='${Status}\n' libboost-all-dev|grep "install ok installed")
    echo Checking for libboost-all-dev: $PKG_LIBBOOST
    if [ "" == "$PKG_LIBBOOST" ]; then
      echo "No libbluetooth-dev. Setting up libboost-all-dev."
      sudo apt-get --force-yes --yes install libboost-all-dev
    fi
	
	PKG_SQLITE3=$(dpkg-query -W --showformat='${Status}\n' sqlite3|grep "install ok installed")
    echo Checking for sqlite3: $PKG_SQLITE3
    if [ "" == "$PKG_SQLITE3" ]; then
      echo "No sqlite3. Setting up sqlite3."
      sudo apt-get --force-yes --yes install sqlite3
    fi
	
	PKG_SQLITE3-DEV=$(dpkg-query -W --showformat='${Status}\n' libsqlite3-dev|grep "install ok installed")
    echo Checking for libsqlite3-dev: $SQLITE3-DEV
    if [ "" == "$SQLITE3-DEV" ]; then
      echo "No libsqlite3-dev. Setting up libsqlite3-dev."
      sudo apt-get --force-yes --yes install libsqlite3-dev
    fi

    PKG_APT_LISTCHANGES=$(dpkg-query -W --showformat='${Status}\n' apt-listchanges|grep "install ok installed")
    echo Checking for apt-listchanges: $PKG_APT_LISTCHANGES
    if [ "install ok installed" == "$PKG_APT_LISTCHANGES" ]; then
      echo "apt-listchanges installed. Removing."
      sudo apt-get --force-yes --yes remove apt-listchanges
    fi

	sudo pip install --upgrade pip
	sudo pip install --upgrade setuptools
	sudo pip install pycrypto
	sudo pip install cryptography
	sudo pip install packaging
	sudo pip install appdirs
	sudo pip install six
	sudo pip install paho-mqtt
	sudo pip install twisted==16.4.1
	sudo pip install circus
	sudo pip install wiringpi2
	sudo pip install astral
	sudo pip install ConcurrentLogHandler
	sudo pip install fabric
    
    exit
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

me=$(whoami)


sudo apt-get update

PKG_PYDEV=$(dpkg-query -W --showformat='${Status}\n' python-dev|grep "install ok installed")
echo Checking for python-dev: $PKG_PYDEV
if [ "" == "$PKG_PYDEV" ]; then
  echo "No python-dev. Setting up python-dev."
  sudo apt-get --force-yes --yes install python-dev
fi

PKG_PYPIP=$(dpkg-query -W --showformat='${Status}\n' python-pip|grep "install ok installed")
echo Checking for python-pip: $PKG_PYPIP
if [ "" == "$PKG_PYPIP" ]; then
  echo "No python3-pip. Setting up python-pip."
  sudo apt-get --force-yes --yes install python-pip
fi

PKG_GIT=$(dpkg-query -W --showformat='${Status}\n' git|grep "install ok installed")
echo Checking for git: $PKG_GIT
if [ "" == "$PKG_GIT" ]; then
  echo "No git. Setting up git."
  sudo apt-get --force-yes --yes install git
fi

PKG_LIBSSL_DEV=$(dpkg-query -W --showformat='${Status}\n' libssl-dev|grep "install ok installed")
echo Checking for libssl-dev: $PKG_LIBSSL_DEV
if [ "" == "$PKG_LIBSSL_DEV" ]; then
  echo "No libssl-dev. Setting up libssl-dev."
  sudo apt-get --force-yes --yes install libssl-dev
fi

PKG_BLUETOOTH=$(dpkg-query -W --showformat='${Status}\n' bluetooth|grep "install ok installed")
echo Checking for bluetooth: $PKG_BLUETOOTH
if [ "" == "$PKG_BLUETOOTH" ]; then
  echo "No bluetooth. Setting up bluetooth."
  sudo apt-get --force-yes --yes install bluetooth
fi

PKG_LIBBLUETOOTH=$(dpkg-query -W --showformat='${Status}\n' libbluetooth-dev|grep "install ok installed")
echo Checking for bluetooth: $PKG_LIBBLUETOOTH
if [ "" == "$PKG_LIBBLUETOOTH" ]; then
  echo "No libbluetooth-dev. Setting up libbluetooth-dev."
  sudo apt-get --force-yes --yes install libbluetooth-dev
fi

PKG_LIBBOOST=$(dpkg-query -W --showformat='${Status}\n' libboost-all-dev|grep "install ok installed")
echo Checking for libboost-all-dev: $PKG_LIBBOOST
if [ "" == "$PKG_LIBBOOST" ]; then
  echo "No libbluetooth-dev. Setting up libboost-all-dev."
  sudo apt-get --force-yes --yes install libboost-all-dev
fi

PKG_SQLITE3=$(dpkg-query -W --showformat='${Status}\n' sqlite3|grep "install ok installed")
echo Checking for sqlite3: $PKG_SQLITE3
if [ "" == "$PKG_SQLITE3" ]; then
  echo "No sqlite3. Setting up sqlite3."
  sudo apt-get --force-yes --yes install sqlite3
fi

PKG_SQLITE3-DEV=$(dpkg-query -W --showformat='${Status}\n' libsqlite3-dev|grep "install ok installed")
echo Checking for libsqlite3-dev: $SQLITE3-DEV
if [ "" == "$SQLITE3-DEV" ]; then
  echo "No libsqlite3-dev. Setting up libsqlite3-dev."
  sudo apt-get --force-yes --yes install libsqlite3-dev
fi
PKG_APT_LISTCHANGES=$(dpkg-query -W --showformat='${Status}\n' apt-listchanges|grep "install ok installed")
echo Checking for apt-listchanges: $PKG_APT_LISTCHANGES
if [ "install ok installed" == "$PKG_APT_LISTCHANGES" ]; then
  echo "apt-listchanges installed. Removing."
  sudo apt-get --force-yes --yes remove apt-listchanges
fi

sudo pip install --upgrade pip
sudo pip install --upgrade setuptools
sudo pip install pycrypto
sudo pip install cryptography
sudo pip install packaging
sudo pip install appdirs
sudo pip install six
sudo pip install paho-mqtt
sudo pip install twisted==16.4.1
sudo pip install circus
sudo pip install astral
sudo pip install wiringpi2
sudo pip install ConcurrentLogHandler
sudo pip install fabric

exit