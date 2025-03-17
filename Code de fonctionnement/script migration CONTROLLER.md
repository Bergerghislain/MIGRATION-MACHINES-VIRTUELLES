SCRIPT DE MIGRATION A INTEGRER AU NIVEAU DU CONTROLLER:

#!/bin/bash

# Script : openstack-migrate.sh
# Usage : ./openstack-migrate.sh <vm_id> <source_host> <target_host>

VM_ID=$1
SOURCE_CLUSTER=$2
TARGET_CLUSTER=$3
JSON_FILE="/chemin/absolu/webmail.grenoble-inp.org.txt"

# Récupération du statut depuis le JSON
check_migration() {
  jq -r --arg src "$SOURCE_CLUSTER" --arg dst "$TARGET_CLUSTER" \
  '.[$src][$dst] // {"success": false, "info": "Combinaison cluster non documentée"}' $JSON_FILE
}

# Exécuter la vérification
RESULT=$(check_migration)
SUCCESS=$(echo $RESULT | jq -r '.success')
INFO=$(echo $RESULT | jq -r '.info')

if [ "$SUCCESS" == "true" ]; then
  # Lancer la migration live avec OpenStack CLI
  openstack server migrate --live $TARGET_CLUSTER $VM_ID --wait
  echo "Migration réussie vers $TARGET_CLUSTER"
else
  echo "ERREUR: Migration impossible - $INFO"
  exit 1
fi
