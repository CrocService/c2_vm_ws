# CROC Cloud (C2) VM management Web-Service

[![Build Status](https://travis-ci.org/avmaximov/c2_vm_ws.svg?branch=master)](https://travis-ci.org/avmaximov/c2_vm_ws)

Simple Flask web service for management VMs at CROC Cloud using REST API.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Environment variables](#environment-variables)

## Installation

```sh
git clone https://github.com/avmaximov/c2_vm_ws
cd c2_vm_ws
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run this service as standalone app, download c2rc.sh (https://console.cloud.croc.ru/c2rc.sh) inside the *c2_vm_ws* folder, and use the following commands:


```sh
cd c2_vm_ws
source venv/bin/activate
source c2rc.sh
./c2_vm_ws.py

```

## Running as WSGI app

To run this service as .wsgi app, add VirtualHost to your Apache server with the following configuration:

```apacheconf
<VirtualHost *>
    ServerName example.com

    SetEnv MAILSERVER_WS_TOKEN "TZCBgcRYW3BYITzL+mQj+t1aXINxn1aasdfasfas8lsBlcvPWdqUOCWTrBWGzoDLkgTUoM792gtzrPDhQ=="

    WSGIDaemonProcess application user=user1 group=group1 threads=5
    WSGIScriptAlias / /var/www/c2_vm_ws/c2_vm_ws.wsgi

    <Directory /var/www/c2_vm_ws>
        WSGIProcessGroup application
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```

## Building container

Use *build.sh* script to build Docker container

```sh
cd c2_vm_ws
./build.sh
```

# Environment variables

| Variable       | Description | Default value |
| -------------- | ----------- | ------------- |
| APP_TOKEN | Application securing token (see, Securing API endpoints(#securing-api-endpoints)) | Not set |
| EC2_URL | API url to connect to (look at c2rc.sh content) | https://api.cloud.croc.ru |
| EC2_ACCESS_KEY | EC2 Access Key | Look at c2rc.sh content |
| EC2_SECRET_KEY | EC2 Secret Key | Look at c2rc.sh content |
| VPC | VPC where to lauch instances | vpc-3EDDC900 |
| TEMPLATE | Template to be used to launch instances from | cmi-2A21A30D |
| INSTANCE_TYPE | VM size | c1.large |
| SECURITY_GROUP | ID of external subnet where to manage instances (look at ```c2-ec2 DescribeSecurityGroups``` output) | subnet-61ECBB2A |
| KEY_NAME | Public SSH key name used during instances start | Lenovo-T410 |
| DEBUG | Enable Falsk debug output | True |

## Launching container

```sh
docker run --name c2_vm_ws --rm -p 8080:5000 --e TEMPLATE="cmi-2A21A30D" -e DEBUG="False" -e EC2_URL=$EC2_URL -e EC2_ACCESS_KEY=$EC2_ACCESS_KEY -e EC2_SECRET_KEY=$EC2_SECRET_KEY amaksimov/c2_vm_ws
```

## Securing API endpoints
Setup *MAILSERVER_WS_TOKEN* environment variable with a strong token which will be used
for restricting API endpoints. Strong token generation oneliner:

```sh
python -c 'import os; import base64; print base64.b64encode(os.urandom(64))'
```

API endpoints will be opened if *APP_TOKEN* is not set.

## Accessing WS API endpoint

```sh
echo "Getting VM list:"
curl http://service.isin.digital/api/v1/vms?token=TZCBgcRYW3BYITzL%2BmQj%2Bt1aXINxn1aasdfasfas8lsBlcvPWdqUOCWTrBWGzoDLkgTUoM792gtzrPDhQ%3D%3D

echo "Launching new VM:"
curl -d '{"template_id":"cmi-2A21A30D", "key_name":"Lenovo-T410", "instance_type":"c1.large", "security_group":"subnet-61ECBB2A"}' -H "Content-Type: application/json" -X POST http://service.isin.digital/api/v1/vms?token=TZCBgcRYW3BYITzL%2BmQj%2Bt1aXINxn1aasdfasfas8lsBlcvPWdqUOCWTrBWGzoDLkgTUoM792gtzrPDhQ%3D%3D

echo "Updating VM"
echo "Not implemented"

echo "Deleting VM: i-AB6C31A1"
curl -H "Content-Type: application/json" -X DELETE "http://service.isin.digital/api/v1/vms/i-AB6C31A1?token=TZCBgcRYW3BYITzL%2BmQj%2Bt1aXINxn1aasdfasfas8lsBlcvPWdqUOCWTrBWGzoDLkgTUoM792gtzrPDhQ%3D%3D"
```

You may use

```sh
python -c "import sys; import urllib; a={'token':'TZCBgcRYW3BYITzL+mQj+t1aXINxn1aasdfasfas8lsBlcvPWdqUOCWTrBWGzoDLkgTUoM792gtzrPDhQ=='}; print urllib.urlencode(a)"
```

to urlencode base64 encoded token.
