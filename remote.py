#!/bin/usr/env python

"""
Functions for handling remote AWS EC2 instances, security groups and key pairs.

http://boto3.readthedocs.io/en/latest/index.html
"""

import os
import sys
import time
import configparser

import requests
import boto3
from botocore.exceptions import ClientError


config_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)
key, val = config.get('AWS', 'instance_tag').split(':')
my_tag = {"Key" : key, "Value" : val}
kn = config.get('AWS', 'keypair_name')
gn = config.get('AWS', 'secgroup_name')
image_id = config.get('AWS', 'image_id')
instance_type = config.get('AWS', 'instance_type')

ec2 = boto3.resource('ec2')


def get_my_ip():
    'Get my own public ip.'

    my_ip = requests.get('http://checkip.amazonaws.com').text.strip()
    print('found my public IP: "%s"' % my_ip)
    return my_ip


def create_keypair():
    'Create key pair if not existing already plus .pem file.'

    try:
        list(ec2.key_pairs.filter(KeyNames=[kn]))
        print('AWS key pair named "%s" already exists' % kn)
    except ClientError:
        keypair = ec2.create_key_pair(KeyName=kn, DryRun=False)
        print('created AWS key pair named "%s"' % keypair.name)
        km = keypair.key_material
        path = '%s.pem' % kn
        open(path, 'w').write(km)
        print('created file "%s"' % path)
        os.chmod(path, 0o400)
        print('chmod to 400 for file "%s"' % path)


def list_keypair():
    'Check keypair.'

    try:
        list(ec2.key_pairs.filter(KeyNames=[kn]))
    except ClientError:
        pass
    else:
        for kp_info in ec2.key_pairs.filter(KeyNames=[kn]):
            print('found AWS key pair named "%s"' % kp_info.name)


def delete_keypair():
    'Delete key pair.'

    try:
        list(ec2.key_pairs.filter(KeyNames=[kn]))
    except ClientError:
        print('AWS key pair named "%s" does not exist' % kn)
    else:
        for kp_info in ec2.key_pairs.filter(KeyNames=[kn]):
            kp_info.delete()
            print('deleted AWS key pair named "%s"' % kp_info.name)

        path = '%s.pem' % kn
        os.chmod(path, 0o600)
        print('chmod to 600 for file "%s"' % path)
        os.remove(path)
        print('removed file "%s"' % path)


def create_security_group():
    'Create security group if not existing already.'

    my_ip = get_my_ip()
    try:
        sec_groups = list(ec2.security_groups.filter(GroupNames=[gn]))
        print('security group named "%s" already exists' % gn)
        # add my current IP since that might have changed between now 
        # and the last time this sec grp was created 
        sec_groups[0].authorize_ingress(
            IpProtocol="tcp", 
            CidrIp="%s/32" % my_ip, 
            FromPort=22, 
            ToPort=22, 
            DryRun=False)
    except ClientError:
        sec_group = ec2.create_security_group(
            GroupName=gn, 
            Description='mobility challenge', 
            DryRun=False)
        print('created security group named "%s"' % sec_group.group_name)
        sec_group.authorize_ingress(
            IpProtocol="tcp", 
            CidrIp="%s/32" % my_ip, 
            FromPort=22, 
            ToPort=22, 
            DryRun=False)
        sec_group.authorize_ingress(
            IpProtocol="tcp", 
            CidrIp="0.0.0.0/0", 
            FromPort=5000, 
            ToPort=5000, 
            DryRun=False)
        print('created inbound access rules for security group named "%s"' % sec_group.group_name)


def list_security_group():
    'Check security group.'

    try:
        list(ec2.security_groups.filter(GroupNames=[gn]))
    except ClientError:
        pass
    else:
        for sg in ec2.security_groups.filter(GroupNames=[gn]):
            print('found AWS security group named "%s"' % sg.group_name)


def delete_security_group():
    'Delete existing security group.'

    try:
        list(ec2.security_groups.filter(GroupNames=[gn]))
    except ClientError:
        pass
    else:
        for sg in ec2.security_groups.filter(GroupNames=[gn]):
            sg.delete()
            print('security group named "%s" deleted' % gn)


def create_instance():
    'Create new instance, if not already existing.'

    instances = ec2.instances.filter(Filters=[
        {'Name': "tag:%s" % my_tag['Key'], 'Values': [my_tag['Value']]}, 
        {'Name': 'instance-state-name', 'Values': ['running']}])
    if list(instances):
        for i in list(instances):
            print('instance with id "%s" already exists' % i.id)
        config.set('AWS', 'instance_id', i.id)
    else:
        instances = ec2.create_instances(
            ImageId=image_id, 
            InstanceType=instance_type, 
            KeyName=kn, 
            SecurityGroups=[gn], 
            MinCount=1, 
            MaxCount=1,
            DryRun=False)
        print('created instance with id "%s"' % instances[0].id)
        config.set('AWS', 'instance_id', instances[0].id)
        config.write(open(config_path, 'w'))

    # tag instance
    for i in instances:
        ec2.create_tags(Resources=[i.id], Tags=[my_tag])
        print('tagged instance "%s" with tag "%s"' % (i.id, str(my_tag)))


def get_instance_public_ip():
    "Get public ip address of the instance (assuming there's only one)."

    instances = ec2.instances.filter(Filters=[
        {'Name': "tag:%s" % my_tag['Key'], 'Values': [my_tag['Value']]}, 
        {'Name': 'instance-state-name', 'Values': ['running']}])
    i = None
    for i in instances:
        pass
    if not i is None:
        public_ip = i.public_ip_address
        print('instance "%s" has public IP "%s"' % (i.id, public_ip))
        config.set('AWS', 'instance_ip', public_ip)
        config.write(open(config_path, 'w'))
        return public_ip


def list_instance():
    'Check running instances.'

    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for i in instances:
        print('found instance %s %s' % (i.id, i.instance_type))


# buggy...
def delete_instance():
    'Delete instance.'

    instances = ec2.instances.filter(Filters=[
        {'Name': "tag:%s" % my_tag['Key'], 'Values': [my_tag['Value']]}, 
        {'Name': 'instance-state-name', 'Values': ['running']}
    ])
    i = None
    ids = [i.id for i in instances]
    ec2.instances.filter(InstanceIds=ids).stop()
    if i:
        print('instance "%s" stopped' % i.id)
        time.sleep(3)
    ec2.instances.filter(InstanceIds=ids).terminate()
    if i:
        print('instance "%s" terminated' % i.id)
        time.sleep(3)
    # must wait util done...
    config.set('AWS', 'instance_id', '')
    config.set('AWS', 'instance_ip', '')
    config.write(open(config_path, 'w'))


def show_usage():
    prog = os.path.basename(sys.argv[0])
    print('Usage: %s create | list | delete' % prog)
    sys.exit(0)


if __name__ == '__main__':
    try:
        arg = sys.argv[1]
    except IndexError:
        show_usage()
    if arg == 'create':
        create_keypair()
        create_security_group()
        create_instance()
        while True:
            time.sleep(3)
            ip = get_instance_public_ip()
            if ip:
                print('created instance has public IP: %s' % ip)
                break
    elif arg == 'list':
        list_keypair()
        list_security_group()
        list_instance()
        public_ip = get_instance_public_ip()
        if public_ip:
            print('instance has public IP: %s' % public_ip)
            cmd = "ssh -i %s.pem admin@%s" % (kn, public_ip)
            print('use this command to login via ssh: %s' % cmd)
    elif arg == 'delete':
        delete_instance()
        while True:
            time.sleep(3)
            ip = get_instance_public_ip()
            if ip is None:
                break
            # not enough; we must wait until status is really "terminated"...
        delete_security_group()
        delete_keypair()
    else:
        show_usage()
