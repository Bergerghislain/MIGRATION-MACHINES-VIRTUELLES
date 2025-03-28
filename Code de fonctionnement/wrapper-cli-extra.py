import csv
import json
import subprocess
import logging
import argparse
from typing import Dict, Any

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='openstack_migration.log'
)

def get_vm_host(vm_id: str) -> str:
    """Récupère l'hôte actuel d'une VM via OpenStack CLI"""
    cmd = [
        'openstack', 'server', 'show', vm_id,
        '-c', 'OS-EXT-SRV-ATTR:hypervisor_hostname',
        '-f', 'value'
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de la récupération de l'hôte : {e.stderr}")
        raise

def get_cluster_details(host: str) -> Dict[str, Any]:
    """Récupère les détails du cluster depuis le CSV enrichi"""
    with open('/etc/node-clusters.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['hostname'] == host:
                return {
                    'cluster': row['cluster'],
                    'vlan': row['vlan'],
                    'xen_version': row['xen_version'],
                    'cpu_flags': row['cpu_flags'].split(';')
                }
        raise ValueError(f"Hôte {host} non trouvé dans le CSV")

def check_xen_compatibility(source_host: str, target_host: str) -> bool:
    """Vérifie la compatibilité Xen via SSH"""
    try:
        # Récupération des informations Xen
        cmd_source = f"ssh {source_host} xl info | grep -E 'xen_version|cc_compiler'"
        cmd_target = f"ssh {target_host} xl info | grep -E 'xen_version|cc_compiler'"
        
        source_info = subprocess.run(cmd_source, shell=True, capture_output=True, text=True)
        target_info = subprocess.run(cmd_target, shell=True, capture_output=True, text=True)
        
        return source_info.stdout == target_info.stdout
        
    except Exception as e:
        logging.error(f"Échec vérification Xen : {str(e)}")
        return False

def check_network_compatibility(source_vlan: str, target_vlan: str) -> bool:
    """Vérifie la connectivité réseau entre VLANs"""
    cmd = f"openstack network show --vlan {source_vlan} -c subnets -f value"
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        source_subnet = result.stdout.strip()
        return source_subnet in get_routed_subnets(target_vlan)
    except Exception as e:
        logging.error(f"Échec vérification réseau : {str(e)}")
        return False

def migrate_vm(vm_id: str, target_host: str, dry_run: bool = False) -> None:
    """Fonction principale de migration avec vérifications"""
    try:
        # Récupération des informations
        source_host = get_vm_host(vm_id)
        source_details = get_cluster_details(source_host)
        target_details = get_cluster_details(target_host)
        
        # Chargement des règles de migration
        with open('/etc/openstack/migration_rules.json') as f:
            migration_rules = json.load(f)
        
        # Vérification multi-couches
        checks = {
            'json_rule': migration_rules.get(source_details['cluster'], {})
                .get(target_details['cluster'], {}).get('success', False),
            'xen': check_xen_compatibility(source_host, target_host),
            'network': check_network_compatibility(
                source_details['vlan'], 
                target_details['vlan']
            ),
            'cpu': set(source_details['cpu_flags']).issubset(
                set(target_details['cpu_flags'])
            )
        }
        
        # Logique de décision
        if all(checks.values()):
            if dry_run:
                logging.info(f"DRY RUN: Migration de {vm_id} vers {target_host} possible")
                return
                
            cmd = [
                'openstack', 'server', 'migrate',
                '--live', target_host, vm_id, '--wait'
            ]
            subprocess.run(cmd, check=True)
            logging.info(f"Migration réussie de {vm_id} vers {target_host}")
            
        else:
            failed = [k for k, v in checks.items() if not v]
            msg = f"Migration bloquée - Échec: {', '.join(failed)}"
            logging.warning(msg)
            print(msg)
            
    except Exception as e:
        logging.error(f"Erreur critique: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('vm_id', help='ID de la VM à migrer')
    parser.add_argument('target_host', help='Hôte de destination')
    parser.add_argument('--dry-run', action='store_true', help='Simulation')
    args = parser.parse_args()
    
    migrate_vm(args.vm_id, args.target_host, args.dry_run)
