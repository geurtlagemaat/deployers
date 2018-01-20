########################################
"""
Fabfile to create Generic Bliknet Environment
- create user. Set passwrd with:
    sudo su -
    passwd bliknet
- create base structure
- create a virtualenv for Circus
- install Circus Process Manager

And Bliknet specific Apps
Each Bliknet app has it's own VirtualEnv environment

# CANDO
Install SMAData app
Mount NAS
Copy settings etc from NAS
"""
########################################

from fabric.api import *
import time
import os

SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

import common

env.hosts = ['localhost']

DEFAULT_USER = 'bliknet'
DEFAULT_GROUP = 'bliknet'
VIRTUAL_ENV_NAME = 'virtualenv'
BLIKNET_BASE_DIR = '/opt/bliknet'

CIRCUS_BASE_DIR = os.path.join(BLIKNET_BASE_DIR, 'circus')
CIRCUS_VIRTUAL_ENV_LOCATION = os.path.join(CIRCUS_BASE_DIR, VIRTUAL_ENV_NAME)
CIRCUS_APPS_CONFIGS = os.path.join(CIRCUS_BASE_DIR,'config','apps')

GIT_BASE_URL = 'https://github.com/geurtlagemaat/'
# Apps and there names name must equal git repos name!
LIVING_APP_DIR = 'living'
RGBCONTROLLER_APP_DIR = 'RGBController'
ENERGYLOGGER_APP_DIR = 'pilogger'
WEATHERLOGGER_APP_DIR = 'weatherstation'
SAUNACONTROL_APP_DIR = 'saunacontroller'
# TODO: streamer
# TODO: netchecker
# TODO: cam2video


#######################
## Core server setup ##
#######################

def install_start():
    """ Notify of install start """
    print("* Warning *")
    print("""The primary use of this installer is to prepare a Bliknet environment for a new Bliknet Node""")
    time.sleep(10)
    print("Installer is starting...")
    # print("OS will reboot when the installer is complete.")
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
    """Install Circus using a virtual env. Create directure structure for future Bliknet App Configs
       Install as a systemd service.
    """
    common.forcedir(location=BLIKNET_BASE_DIR, dirname='circus', user=DEFAULT_USER, group=DEFAULT_GROUP)
    common.create_venv(location=CIRCUS_BASE_DIR, name=VIRTUAL_ENV_NAME, user=DEFAULT_USER)
    common.forcedir(location=CIRCUS_BASE_DIR, dirname='config', user=DEFAULT_USER, group=DEFAULT_GROUP)
    # create the location for the Apps configs to be installed later
    common.forcedir(location=os.path.join(CIRCUS_BASE_DIR,'config'), dirname='apps', user=DEFAULT_USER, group=DEFAULT_GROUP)

    with cd(CIRCUS_VIRTUAL_ENV_LOCATION):
        sudo("source %s/bin/activate && pip install circus" % CIRCUS_VIRTUAL_ENV_LOCATION, user=DEFAULT_USER)
        sudo("source %s/bin/activate && pip install circus-web" % CIRCUS_VIRTUAL_ENV_LOCATION, user=DEFAULT_USER)
    sudo('cp %s %s' % (os.path.join(SCRIPT_DIR, 'circus-config/circus.ini'), os.path.join(CIRCUS_BASE_DIR, 'config')))
    sudo('cp %s %s' % (os.path.join(SCRIPT_DIR, 'scripts/*.sh') ,CIRCUS_BASE_DIR), user=DEFAULT_USER)
    sudo('chmod 700 %s/*.sh' % CIRCUS_BASE_DIR)
    # OS Auto start with systemd
    sudo('sudo cp %s /etc/systemd/system/circus.service'.format(**env) % os.path.join(SCRIPT_DIR,
                                                                                      'scripts/circus.service'))
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

def install_bliknet_lib(virtualenvPath):
    with cd('/tmp'):
        sudo("git clone --branch master https://github.com/geurtlagemaat/bliknetlib.git", user=DEFAULT_USER)
        with cd('bliknetlib'):
            sudo("source %s/bin/activate && pip install -r requirements.txt" % virtualenvPath, user=DEFAULT_USER)
            sudo("source %s/bin/activate && python setup.py install" % virtualenvPath, user=DEFAULT_USER)
    with cd('/tmp'):
        sudo("rm -rf bliknetlib", user=DEFAULT_USER)
@task
def install_generic_bliknet_app(appdir):
    print("* Warning *")
    print("""This installer will install Bliknet %s App""" % appdir)
    time.sleep(5)
    print("Installer is starting...")
    common.forcedir(location=BLIKNET_BASE_DIR, dirname=appdir, user=DEFAULT_USER, group=DEFAULT_GROUP)
    common.create_venv(location=os.path.join(BLIKNET_BASE_DIR, appdir), name=VIRTUAL_ENV_NAME, user=DEFAULT_USER)
    install_bliknet_lib(virtualenvPath=os.path.join(BLIKNET_BASE_DIR, appdir, VIRTUAL_ENV_NAME))
    gitURL = GIT_BASE_URL + appdir + '.git'
    with cd('/tmp'):
        sudo("git clone --branch master %s" % gitURL, user=DEFAULT_USER)
        with cd(appdir):
            sudo("source %s/bin/activate && pip install -r requirements.txt" % os.path.join(BLIKNET_BASE_DIR, appdir, VIRTUAL_ENV_NAME), user=DEFAULT_USER)
    with cd('/tmp'):
        sudo("mv %s/ %s " % (appdir, os.path.join(BLIKNET_BASE_DIR, appdir, 'app')), user=DEFAULT_USER)
        sudo("mv %s/circus/*.ini %s" % (os.path.join(BLIKNET_BASE_DIR, appdir, 'app'), CIRCUS_APPS_CONFIGS), user=DEFAULT_USER)
        sudo("rm -rf %s" % appdir, user=DEFAULT_USER)
    # TODO: Mount NAS, Copy settings file

@task
def install_bliknet_living_app():
    # git clone https://github.com/adafruit/Adafruit_Python_DHT
    # sudo apt-get install python-dev
    install_generic_bliknet_app(LIVING_APP_DIR)
    with cd('/tmp'):
        sudo("git clone --branch master %s" % "https://github.com/adafruit/Adafruit_Python_DHT.git", user=DEFAULT_USER)
        with cd("Adafruit_Python_DHT"):
            sudo("source %s/bin/activate && python setup.py install" % os.path.join(BLIKNET_BASE_DIR, LIVING_APP_DIR, VIRTUAL_ENV_NAME), user=DEFAULT_USER)

@task
def install_bliknet_energylogger_app():
    install_generic_bliknet_app(ENERGYLOGGER_APP_DIR)

@task
def install_bliknet_RGBController_app():
    install_generic_bliknet_app(RGBCONTROLLER_APP_DIR)

@task
def install_bliknet_weatherlogger_app():
    install_generic_bliknet_app(WEATHERLOGGER_APP_DIR)

