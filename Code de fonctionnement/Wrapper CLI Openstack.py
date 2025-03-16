//Wrapper Openstack CLI

import csv
import json
import subprocess

def get_cluster(host):
    with open('/etc/node-clusters.csv') as f:
        return next(row[1] for row in csv.reader(f) if row[0] == host)

def migrate_vm(vm_id, target_host):
    source_host = get_vm_host(vm_id)
    source_cluster = get_cluster(source_host)
    target_cluster = get_cluster(target_host)
    
    with open('/chemin/webmail.grenoble-inp.org.txt') as f:
        data = json.load(f)
        
    if data.get(source_cluster, {}).get(target_cluster, {}).get('success', False):
        subprocess.run(f"openstack server migrate --live {target_host} {vm_id}", shell=True)
    else:
        print(f"Blocked: {data[source_cluster][target_cluster]['info']}")

