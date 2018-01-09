"""Shared functions for Fabric scripts"""
import os
import zipfile
import shutil
import time
import string
import random
from os.path import join
from posixpath import join as posixjoin
from contextlib import closing

from fabric.api import run, cd, sudo, env
from fabric.decorators import task

@task
def update_upgrade():
    """ Update OS """
    sudo("apt-get update")
    sudo("apt-get upgrade -y")

def create_venv(location, name, user):
    with cd(location):
        sudo("virtualenv -p python %s" % name, user=user)

def forcedir(location, dirname, user, group):
    # TODO check ownership
    if os.path.isdir(location):
        if os.path.isdir(os.path.join(location,dirname)):
            print "given base location %s has already a %s folder." % (location,dirname)
        else:
            with cd("location"):
                sudo("mkdir %s" % dirname)
                sudo("chown %s:%s %s" % (user, group, dirname))
    else:
        print "given base location %s does not exists" % location

def generate_password(length=8):
    """Generate a random password with the given length"""
    chars = string.ascii_letters + string.digits
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for _ in range(length))

def collect_requirements(requirements_path, repository_path, target_path):
    """Copy requirement packages, also creating a list of filenames of packages that should be installed."""
    required_filenames = get_dependency_filenames(requirements_path, repository_path)
    os.makedirs(target_path)
    with open(join(target_path, 'requirement-filenames.txt'), 'w') as f:
        for fn in required_filenames:
            shutil.copy(fn, target_path)

            f.write('%s\n' % os.path.basename(fn))

    filter_requirements(requirements_path, os.path.join(target_path, 'filtered-requirements.txt'))

def install_virtualenv_contents_setup(venv_path, package_repository_path, package_list_path):
    """Install or upgrade requirements into an existing virtualenv using setup.py"""
    # Create temporary working directory
    work_dir = sudo('mktemp -d')

    # Read contents of file with package names
    reqs_file_contents = run('cat "{package_list_path}"'.format(**locals()))

    for fn in reqs_file_contents.split('\n'):
        fn = fn.strip()
        if fn == '':
            continue

        # Unpack the package into the temporary directory
        with cd(work_dir):
            sudo(get_extract_command(posixjoin(package_repository_path, fn)))

        # Run setup.py from extracted package
        package_name = remove_package_extension(fn)
        extracted_package_dir = posixjoin(work_dir, package_name)
        with cd(extracted_package_dir):
            log_name = posixjoin(work_dir, package_name + '.log')
            sudo('{venv_path}/bin/python setup.py install > {log_name} 2>&1'.format(**locals()))

def install_virtualenv_contents_pip(venv_path, package_repository_path, requirements_path):
    """Install or upgrade requirements into an existing virtualenv using PIP"""
    sudo(('{venv_path}/bin/pip install -r {requirements_path} --no-index '
          '--find-links {package_repository_path}').format(**locals()))

def get_dependency_filenames(requirements_path, package_repository_path):
    """Return a list of Python packages file names to install for the given instance"""
    res = []

    package_map = get_package_map(package_repository_path)

    for line in open(requirements_path):
        package, version = parse_requirement(line)

        if package is None or version is None:
            continue
        if package in env.get('skip_reqs', []):
            continue

        package_key = '%s-%s' % (package, version)

        try:
            package_file = package_map[package_key]
            res.append(package_file)
        except KeyError as exc:
            raise Exception('Could not find file for dependency %s' % exc)

    return res

def filter_requirements(requirements_path, filtered_requirements_path):
    with open(filtered_requirements_path, 'w') as filtered_file:
        for line in open(requirements_path):
            package, version = parse_requirement(line)
            if package is None or version is None:
                continue
            if package not in env.get('skip_reqs', []):
                filtered_file.write(line)


def remove_comments(line):
    """Remove comments, meaning everything after the first #"""
    return line.split('#', 1)[0].strip()

def parse_requirement(line):
    """Return a tuple of a package name and version number for the given requirements line

    Returns None, None if the line could not be parsed

    Only supports "==" version specifications for now
    """
    line = remove_comments(line)
    try:
        package, version = line.split('==')
    except ValueError:
        return None, None
    else:
        return package.strip().lower(), version.strip().lower()

class UnknownExtensionException(Exception):
    pass

PACKAGE_EXTRACT_COMMANDS = {
    '.tar.gz': 'tar xfz "%s"',
    '.tgz': 'tar xfz "%s"',
    '.tar.bz2': 'tar xfj "%s"',
    '.zip': 'unzip -q "%s"',
}

def remove_package_extension(fn):
    """Remove extension from given package filename"""
    for ext in PACKAGE_EXTRACT_COMMANDS.keys():
        if fn.lower().endswith(ext):
            return fn[:-len(ext)]

    raise UnknownExtensionException('Package file %s has unknown extension' % fn)

def get_extract_command(fn):
    """Return the command needed to unpack the given file"""
    for ext, cmd in PACKAGE_EXTRACT_COMMANDS.iteritems():
        if fn.lower().endswith(ext):
            return cmd % fn

    raise UnknownExtensionException("Don't know how to unpack file %s" % fn)

def get_package_map(package_repository_path):
    """Return a dict that maps package names to package filename paths

    Each key is the lowercase package name without the extension, e.g.
    twisted-16.3.0"""
    repository_files = os.listdir(package_repository_path)

    res = {}

    for fn in repository_files:
        try:
            package_key = remove_package_extension(fn).lower()
        except UnknownExtensionException:
            pass
        else:
            res[package_key] = join(package_repository_path, fn)

    return res

def add_dir_to_zip(zip_file_path, path_to_add, prefix=None,
                   ext_blacklist=None, ext_whitelist=None):
    """Add all files below path_to_add to a zipfile at zip_file_path

    Note that the archive is appended to, so if you want to start with an empty
    archive, remove the file first.

    If prefix is supplied, all file paths in the file are prefixed with that
    string.

    Files having an extension in ext_blacklist are not added to the archive.
    """
    if ext_blacklist is None:
        ext_blacklist = ['.pyc', '.log']
    with closing(zipfile.ZipFile(zip_file_path, 'a', zipfile.ZIP_DEFLATED)) as zipFile:
        for root, _dirs, files in os.walk(path_to_add):
            for fileName in files:
                _, ext = os.path.splitext(fileName)
                if ext_blacklist is not None and ext in ext_blacklist:
                    continue

                if ext_whitelist is not None and ext not in ext_whitelist:
                    continue

                filePath = os.path.join(root, fileName)
                arcname = os.path.relpath(filePath, path_to_add)

                if prefix is not None:
                    arcname = prefix + arcname
                zipFile.write(filePath, arcname)

class sudosu:
    """Run commands as other user using "sudo su - <username>" """
    def __init__(self, user):
        self.user = user

    def __enter__(self):
        self.old_sudo_prefix = env.sudo_prefix
        self.old_sudo_user, env.sudo_user = env.sudo_user, self.user
        env.sudo_prefix = "sudo -S -p '%(sudo_prompt)s' su - %(sudo_user)s -c"

    def __exit__(self, a, b, c):
        env.sudo_prefix = self.old_sudo_prefix
        env.sudo_user = self.old_sudo_user
