#!/usr/bin/env python

import crypt
import os
import time
import random
import string
import pprint
from functools import wraps
import boto
from flask import Flask, jsonify, request, abort

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

pp = pprint.PrettyPrinter(indent=4)

def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # Just pass all requests if there's no APP_TOKEN
        if APP_TOKEN is None:
            return view_function(*args, **kwargs)
        if request.args.get('token') and request.args.get('token') == APP_TOKEN:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function

application = Flask(__name__)

DEFAULT_EC2_URL = 'https://api.cloud.croc.ru'
DEFAULT_VPC = 'vpc-3EDDC900'
DEFAULT_TEMPLATE = 'cmi-2A21A30D'
DEFAULT_INSTANCE_TYPE = 'c1.large'
DEFAULT_SECURITY_GROUP = 'subnet-61ECBB2A'
DEFAULT_KEY_NAME = 'Lenovo-T410'
DEFAULT_DEBUG = True

try:
    APP_TOKEN = os.environ['APP_TOKEN']
    EC2_URL = os.environ['EC2_URL'] or DEFAULT_EC2_URL
    EC2_ACCESS_KEY = os.environ['EC2_ACCESS_KEY']
    EC2_SECRET_KEY = os.environ['EC2_SECRET_KEY']
    VPC = os.environ['VPC'] or DEFAULT_VPC
    TEMPLATE = os.environ['TEMPLATE'] or DEFAULT_TEMPLATE
    INSTANCE_TYPE = os.environ['INSTANCE_TYPE'] or DEFAULT_INSTANCE_TYPE
    SECURITY_GROUP = os.environ['SECURITY_GROUP'] or DEFAULT_SECURITY_GROUP
    KEY_NAME = os.environ['KEY_NAME'] or DEFAULT_KEY_NAME
    if os.environ['DEBUG'] == 'False':
        DEBUG = False
    elif os.environ['DEBUG'] == 'True':
        DEBUG = True
    else:
        DEBUG = DEFAULT_DEBUG
except:
    APP_TOKEN = os.getenv('APP_TOKEN')
    EC2_URL = os.getenv('EC2_URL') or DEFAULT_EC2_URL
    EC2_ACCESS_KEY = os.getenv('EC2_ACCESS_KEY')
    EC2_SECRET_KEY = os.getenv('EC2_SECRET_KEY')
    VPC = os.getenv('VPC') or DEFAULT_VPC
    TEMPLATE = os.getenv('TEMPLATE') or DEFAULT_TEMPLATE
    INSTANCE_TYPE = os.getenv('INSTANCE_TYPE') or DEFAULT_INSTANCE_TYPE
    SECURITY_GROUP = os.getenv('SECURITY_GROUP') or DEFAULT_SECURITY_GROUP
    KEY_NAME = os.getenv('KEY_NAME') or DEFAULT_KEY_NAME
    if os.getenv('DEBUG') == 'False':
        DEBUG = False
    elif os.getenv('DEBUG') == 'True':
        DEBUG = True
    else:
        DEBUG = DEFAULT_DEBUG


class VmManager(object):
    def __init__(self):
        self.conn = boto.connect_ec2_endpoint(
            EC2_URL,
            aws_access_key_id=EC2_ACCESS_KEY,
            aws_secret_access_key=EC2_SECRET_KEY
        )

    def launch_vm(self, template_id, key_name, instance_type, security_group):
        ips_count = self.get_allocated_ip_addresses_count()
        instances_count = self.get_launched_instaces_count()
        if ips_count <= instances_count:
            self.conn.allocate_address()
        reservation = self.conn.run_instances(
            image_id=template_id,
            key_name=key_name,
            instance_type=instance_type,
            security_groups=[security_group])
        return reservation.instances[0].id

    def delete_vm(self, vm_id):
        instance_address = None
        reservations = self.conn.get_all_instances()
        for r in reservations:
            for inst in r.instances:
                if inst.id == vm_id:
                    instance_address = inst.ip_address
        instance_id = self.conn.terminate_instances(instance_ids=[vm_id])[0].id
        while True:
            if self.get_instance_status(instance_id) == 'terminated':
                break
            time.sleep(1)
        self.conn.release_address(instance_address)

    def list_vms(self):
        data = []
        reservations = self.conn.get_all_instances()#filters=filters)
        for r in reservations:
            for inst in r.instances:
                #pp.pprint(inst.__dict__)
                instance_data = {
                    'id':inst.id,
                    'ip_address': inst.ip_address
                }
                data.append(instance_data)
        return data

    def get_instance_status(self, instance_id):
        reservations = self.conn.get_all_instances()
        for r in reservations:
            for inst in r.instances:
                if instance_id == inst.id:
                    return str(inst.state)
        return None
    def get_launched_instaces_count(self):
        reservations = self.conn.get_all_instances()
        instances_launched = 0
        for r in reservations:
            instances_launched += len(r.instances)
        return instances_launched

    def get_allocated_ip_addresses_count(self):
        eips = self.conn.get_all_addresses()
        addresses_allocated = 0
        addresses_allocated += len(eips)
        return addresses_allocated


def sha512_crypt(password, salt=None, rounds=None):
    if salt is None:
        rand = random.SystemRandom()
        salt = ''.join([rand.choice(string.ascii_letters + string.digits)
                        for _ in range(8)])
        prefix = '$6$'
    if rounds is not None:
        rounds = max(1000, min(999999999, rounds or 5000))
        prefix += 'rounds={0}$'.format(rounds)
    return crypt.crypt(password, prefix + salt)


@application.route("/")
@require_appkey
def hello():

    return 'Hi!'


@application.route('/api/v1/vms', methods=['GET'])
@require_appkey
def getVms():
    manager = VmManager()
    data = manager.list_vms()

    return jsonify(instances=data)


@application.route('/api/v1/vms', methods=['POST'])
@require_appkey
def createVm():
    template_id = request.args.get('template_id', DEFAULT_TEMPLATE)
    key_name = request.args.get('key_name', DEFAULT_KEY_NAME)
    instance_type = request.args.get('instance_type', DEFAULT_INSTANCE_TYPE)
    security_group = request.args.get('security_group', DEFAULT_SECURITY_GROUP)
    manager = VmManager()
    id = manager.launch_vm(template_id, key_name, instance_type, security_group)

    return jsonify(instance={'id':id})


@application.route('/api/v1/vms/<string:id>', methods=['DELETE'])
@require_appkey
def deleteVm(id):
    manager = VmManager()
    manager.delete_vm(id)

    return getVms()


# @application.route('/api/v1/users/<string:email>', methods=['PATCH'])
# @require_appkey
# def updateUser(email):
#     return 'Not implemented'

if __name__ == "__main__":
    application.run(debug=DEBUG, host='0.0.0.0')
