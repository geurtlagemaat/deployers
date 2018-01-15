########################################
"""
Fabfile to create Generic Bliknet Environment
- create user
- create base structure
- create a virtualenv for Circus
- install Circus Process Manager

Depends targets.py
"""
########################################

import sys
from fabric.api import *
import fabric.contrib.files
import time
import os
# from os.path import join
# from posixpath import join as posixjoin

SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

import common  # noqa

BLIKNET_BASE_DIR = '/opt/bliknet'
CIRCUS_BASE_DIR = os.path.join(BLIKNET_BASE_DIR, 'circus')
CIRCUS_VIRTUAL_ENV_NAME = 'virtualenv'
CIRCUS_VIRTUAL_ENV_LOCATION = os.path.join(CIRCUS_BASE_DIR, CIRCUS_VIRTUAL_ENV_NAME)
DEFAULT_USER = 'bliknet'
DEFAULT_GROUP = 'bliknet'

env.hosts = ['localhost']

#######################
## Core server setup ##
#######################

def install_start():
    """ Notify of install start """
    print("* Warning *")
    print("""The primary use of this installer is to prepare a Bliknet environment for a new Bliknet Node""")
    time.sleep(10)
    print("Installer is starting...")
    print("OS will reboot when the installer is complete.")
    time.sleep(5)

@task
def create_bliknet_user():
    """ Create user bliknet and group bliknet on remote server """
    group_exists = False
    user_exists = False

    group_list = run('getent group')
    user_list = run('getent passwd')

    for line in group_list.split('\n'):
        if line.startswith('bliknet:'):
            group_exists = True
            break
    for line in user_list.split('\n'):
        if line.startswith('bliknet:'):
            user_exists = True
            break

    if not group_exists:
        sudo('groupadd --system bliknet')
    else:
        print('Not creating group bliknet: it already exists')
    if not user_exists:
        sudo('useradd --create-home --home-dir /opt/bliknet --gid bliknet --system bliknet')
        # TODO, test!
        sudo(
            'for GROUP in adm dialout cdrom sudo audio video plugdev games users netdev input spi i2c gpio; do sudo adduser bliknet $GROUP; done')
    else:
        print('Not creating user bliknet: it already exists')

@task
def create_root_dirs():
    common.forcedir(location='/opt', dirname='bliknet', user=DEFAULT_USER, group=DEFAULT_GROUP)

def install_syscore():
    # TODO Check
    """ Download and install Host Dependencies. """
    sudo("aptitude install -y build-essential")
    sudo("aptitude install -y python-pip")
    sudo("aptitude install -y python-dev")
    sudo("aptitude install -y python-setuptools")
    sudo("aptitude install -y git")
    sudo("aptitude install -y libssl-dev")
    sudo("aptitude install -y cmake")
    sudo("aptitude install -y libc-ares-dev")
    sudo("aptitude install -y uuid-dev")
    sudo("aptitude install -y daemon")
    sudo("aptitude install -y curl")
    sudo("aptitude install -y net-tools")

def install_pycore():
    sudo("pip install --upgrade pip")
    sudo("pip install virtualenv")

@task
def install_Circus_Process_Manager():
    # config
    common.forcedir(location=BLIKNET_BASE_DIR, dirname='circus', user=DEFAULT_USER, group=DEFAULT_GROUP)
    common.create_venv(location=CIRCUS_BASE_DIR, name=CIRCUS_VIRTUAL_ENV_NAME, user=DEFAULT_USER)
    common.forcedir(location=CIRCUS_BASE_DIR, dirname='config', user=DEFAULT_USER, group=DEFAULT_GROUP)
    # TODO copy generic circus.ini
    # install Circus
    with cd(CIRCUS_VIRTUAL_ENV_LOCATION):
        sudo("source %s/bin/activate && pip install circus" % CIRCUS_VIRTUAL_ENV_LOCATION, user="bliknet")
    sudo('cp %s %s' % (os.path.join(SCRIPT_DIR, 'circus-config/circus.ini')), os.path.join(CIRCUS_BASE_DIR, 'config'))
    # Enable auto start using systemd
    sudo('sudo cp %s /etc/systemd/system/circus.service'.format(**env) % os.path.join(SCRIPT_DIR, 'scripts/circus.service'))
    sudo('sudo chmod 644 /etc/systemd/system/circus.service')
    sudo('sudo systemctl --system daemon-reload')

@task
def create_bliknet_environment():
    install_start()
    common.update_upgrade()
    install_syscore()
    install_pycore()
    create_bliknet_user()
    create_root_dirs()
    install_Circus_Process_Manager()

