#!/bin/bash
# Script : openstack-migrate.sh
# Usage : ./openstack-migrate.sh <vm_id> <target_host> [--dry-run]

VM_ID=$1
TARGET_HOST=$2
DRY_RUN=false
[ "$3" == "--dry-run" ] && DRY_RUN=true

# Configuration
JSON_FILE="/etc/openstack/migration_rules.json"
CSV_FILE="/etc/node-clusters.csv"
LOG_FILE="/var/log/openstack_migration.log"

# Initialisation des logs
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Récupération du cluster source
get_source_cluster() {
    local vm_host=$(openstack server show $VM_ID -c OS-EXT-SRV-ATTR:hypervisor_hostname -f value)
    awk -F, -v host="$vm_host" '$1 == host {print $2}' $CSV_FILE
}

# Vérification réseau
check_network() {
    local source_vlan=$(awk -F, -v cluster="$SOURCE_CLUSTER" '$2 == cluster {print $3}' $CSV_FILE)
    local target_vlan=$(awk -F, -v cluster="$TARGET_CLUSTER" '$2 == cluster {print $3}' $CSV_FILE)
    
    # Vérification directe ou routée
    if [ "$source_vlan" == "$target_vlan" ]; then
        return 0
    else
        openstack router list | grep -q "network:$source_vlan.*network:$target_vlan" && return 0
    fi
    
    log "ERREUR: Aucune route entre VLAN $source_vlan et $target_vlan"
    return 1
}

# Vérification Xen
check_xen() {
    local source_node=$(awk -F, -v cluster="$SOURCE_CLUSTER" '$2 == cluster {print $1; exit}' $CSV_FILE)
    local target_node=$(awk -F, -v cluster="$TARGET_CLUSTER" '$2 == cluster {print $1; exit}' $CSV_FILE)
    
    ssh $source_node "xl info | grep -E 'xen_version|cc_compiler'" > /tmp/xen_source
    ssh $target_node "xl info | grep -E 'xen_version|cc_compiler'" > /tmp/xen_target
    
    if ! diff -q /tmp/xen_source /tmp/xen_target; then
        log "ERREUR: Incompatibilité Xen ($(cat /tmp/xen_source) vs $(cat /tmp/xen_target))"
        return 1
    fi
    return 0
}

# Vérification CPU
check_cpu() {
    local required_flags=$(awk -F, -v cluster="$SOURCE_CLUSTER" '$2 == cluster {print $5}' $CSV_FILE | tr ';' '\n')
    local available_flags=$(awk -F, -v cluster="$TARGET_CLUSTER" '$2 == cluster {print $5}' $CSV_FILE | tr ';' '\n')
    
    for flag in $required_flags; do
        if ! grep -qx "$flag" <<< "$available_flags"; then
            log "ERREUR: Flag CPU manquant ($flag)"
            return 1
        fi
    done
    return 0
}

# Vérification JSON
check_json() {
    local result=$(jq -r --arg src "$SOURCE_CLUSTER" --arg dst "$TARGET_CLUSTER" \
    '.[$src][$dst] // {"success": false, "info": "Combinaison non documentée"}' $JSON_FILE)
    
    success=$(jq -r '.success' <<< "$result")
    info=$(jq -r '.info' <<< "$result")
    
    [ "$success" == "true" ] && return 0
    log "ERREUR: Règle JSON bloque la migration - $info"
    return 1
}

# Main
SOURCE_CLUSTER=$(get_source_cluster)
TARGET_CLUSTER=$(awk -F, -v host="$TARGET_HOST" '$1 == host {print $2}' $CSV_FILE)

log "Début migration $VM_ID de $SOURCE_CLUSTER vers $TARGET_CLUSTER"

# Exécution des vérifications
checks_passed=true
check_network || checks_passed=false
check_xen || checks_passed=false
check_cpu || checks_passed=false
check_json || checks_passed=false

if $checks_passed; then
    if $DRY_RUN; then
        log "DRY RUN: Migration possible"
        exit 0
    fi
    
    if openstack server migrate --live $TARGET_HOST $VM_ID --wait; then
        log "Migration réussie"
        openstack server resize --confirm $VM_ID
        exit 0
    else
        log "Échec de la migration technique"
        exit 1
    fi
else
    log "Migration bloquée - Voir logs détaillés"
    exit 1
fi
