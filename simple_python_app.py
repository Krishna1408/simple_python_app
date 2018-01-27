#!/usr/bin/python3
from flask import Flask, jsonify, request, abort
import time
import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from pprint import pprint


def get_input(inputfile):
    try:
        with open(inputfile, 'r') as input:
            data = input.read()
            return data.split()
    except:
        print ("Please check whether file exist. File name should be %s" % (inputfile))

project_info = get_input('input.txt')
project = project_info[0].split('=')[1]
zone = project_info[1].split('=')[1]
instance_name = project_info[2].split('=')[1]

credentials = GoogleCredentials.get_application_default()
compute = discovery.build('compute', 'v1', credentials=credentials)

app = Flask(__name__)



def create_instance(compute, project, zone, name):
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='debian-cloud', family='debian-8').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()
    image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
    image_caption = "Ready for dessert?"

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                'key': 'startup-script',
                'value': startup_script
            },
                {
                'key': 'url',
                'value': image_url
            }, {
                'key': 'text',
                'value': image_caption
            }]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()

def wait_for_operation(compute, project, zone, operation):
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)




@app.route('/v1/instances/create', methods=['POST'])
def instance_creation():
    
    if not request.json:
        abort(400)

    post_data = request.get_json()
    username = post_data['username']
    password = post_data['password']

    with open('startup.txt', "w") as userdata:
        userdata.write("username=" + username + "\n")
        userdata.write("password=" + password + "\n")

    filenames = ["startup.txt", "append.txt"]
    with open("startup-script.sh", "w") as outfile:
        for fname in filenames:
            with open(fname) as infile:
                content = infile.read()
                outfile.write(content)

    operation = create_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, operation['name'])
    getinstances = compute.instances().get(project=project, zone=zone, instance=instance_name)
    response = getinstances.execute()
    networkIP = (response['networkInterfaces'][0]['networkIP'])
    natIP = (response['networkInterfaces'][0]['accessConfigs'][0]['natIP'])
    post_output = "This is the network IP in GCE: " + networkIP + " \nThis is the nat IP to login to system: " + natIP
    return post_output


@app.route("/")
def hello():
    return "Below methods are supported: \n /healthcheck \n /v1/instances/create \n /v1/delete_instance"

@app.route('/v1/delete_instance', methods=['DELETE'])
def delete_instance():
    delete = compute.instances().delete(
        project=project,
        zone=zone,
        instance=instance_name).execute()
    return "Instance Deletion Initiated, Instance will be deleted in a minute"


@app.route('/healthcheck', methods=['GET'])
def get_healthcheck():
    health_request = compute.instances().get(project=project, zone=zone, instance=instance_name)
    get_health = health_request.execute()
    get_status = get_health["status"]
    if get_status == "RUNNING":
        return ""
    else:
        abort(404)


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
    app.debug = True



