"""
This is used for server provisioning, deploying and starting the service.

Provisioning is done in this case to some AWS EC2 server. And deployment
consists of copying a local development folder to the remote server.

This uses Fabric, since it is simpler than Ansible or Saltstack. Notice
that Fabric currently is still recommended to be used on Python 2! You
can install Fabric with ``pip install fabric``.

Examples:

    fab -l
    fab -h
    fab -i snowdonia.pem -u admin -H 52.57.6.142 provision
    fab -R aws provision
"""

import os
import ConfigParser as configparser

from fabric.api import cd, run, sudo, put, task, env


config_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)

env.key_filename = '%s.pem' % config.get('AWS', 'keypair_name')
user = config.get('AWS', 'instance_user')
port = config.get('SERVICE', 'port')
ip = config.get('AWS', 'instance_ip')
if not ip:
    print('WARNING: No instance_ip found in file "%s"' % config_path)
else:
    env.roledefs = {
        'aws': ['%s@%s' % (user, ip)]
    } 


@task
def provision():
    'Provision remote server.'

    sudo('apt-get update')
    sudo('apt-get install -y emacs') # convenience
    sudo('apt-get install -y bzip2') # needed for unpacking miniconda3
    run('wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh')
    run('bash Miniconda3-latest-Linux-x86_64.sh -b -f -p /home/admin/miniconda3')


@task
def dependencies():
    'Install dependencies on remote server.'

    run('/home/admin/miniconda3/bin/conda update conda')
    run('/home/admin/miniconda3/bin/conda install --yes --quiet basemap')
    run('mkdir -p /home/admin/snowdonia')
    put('requirements.txt', '/home/admin/snowdonia/requirements.txt')
    with cd('/home/admin/snowdonia'):
        run('/home/admin/miniconda3/bin/pip install -r requirements.txt')


@task
def deploy():
    'Deploy code to remote server.'

    run('mkdir -p /home/admin/snowdonia')
    put(os.getcwd(), '/home/admin/')


@task
def serve():
    'Run remote service (until you quit this command!).'

    print('** When this is ready you can open http://%s:%s/ in a webbrowser!' % (ip, port))
    with cd('/home/admin/snowdonia'):
        run('/home/admin/miniconda3/bin/python serve.py')
