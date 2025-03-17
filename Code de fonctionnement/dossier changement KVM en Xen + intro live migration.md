GUIDE D'INSTALLATION DE XEN SUR OPEN STACK:

APRES AVOIR EXECUTE L'INSTALLATION DE OPENSTACK (decrite dans un precedent fichier) sur les noeuds de calcul et sur lr noeud de control je suis le processus suivant : 

---

### **1. Préparation des Nœuds de Compute (Xen Hypervisor)**
#### a. Installer Xen sur les Compute Nodes
```bash
# Se connecter au compute node
ssh root@compute-node

# Installer Xen et ses dépendances

sudo apt update
sudo apt upgrade
sudo apt install -y xen-hypervisor-4.17-amd64 xen-tools

# Configurer GRUB pour démarrer Xen par défaut
sudo sed -i 's/GRUB_DEFAULT=.*/GRUB_DEFAULT="Xen 4.17"/g' /etc/default/grub
sudo update-grub

# Redémarrer le nœud
sudo reboot
```

#### b. Vérifier l'Installation de Xen
Après le redémarrage :
```bash
sudo xl list  # Doit afficher le Domain-0 (Dom0)
```

---

### **2. Configuration d'OpenStack pour Xen**
#### a. Sur le **Controller Node** : Modifier la configuration Nova
```bash
sudo nano /etc/nova/nova.conf
```
Ajoutez ou modifiez ces lignes :
```ini
[DEFAULT]
compute_driver = xenapi.XenAPIDriver  # Pilote Xen pour Nova

[xenserver]
xenapi_connection_url = http://<IP_COMPUTE_NODE>  # IP du compute node Xen
xenapi_connection_username = root
xenapi_connection_password = motdepasserootxen
```

#### b. Sur les **Compute Nodes** : Configurer Nova et Libvirt pour Xen
```bash
sudo nano /etc/nova/nova.conf
```
```ini
[DEFAULT]
compute_driver = xenapi.XenAPIDriver
virt_type = xen
```

Configurer Libvirt :
```bash
sudo nano /etc/libvirt/libvirtd.conf
```
```ini
listen_tls = 0
listen_tcp = 1
auth_tcp = "none"
```

Redémarrer les services :
```bash
sudo systemctl restart nova-compute libvirtd
```

---

### **3. Configurer XenAPI dans DevStack**
Si DevStack est l'outil utilise, ajoutez ces paramètres dans `local.conf` des compute nodes :
```ini
[[post-config|$NOVA_CONF]]
[DEFAULT]
compute_driver = xenapi.XenAPIDriver
xenapi_connection_url = http://<IP_COMPUTE_NODE>
xenapi_connection_username = root
xenapi_connection_password = motdepasserootxen

[libvirt]
virt_type = xen
```

---

### **4. Migration de VMs avec Xen**
#### a. Prérequis pour les Migrations
- **Stockage partagé** : Les images des VMs doivent être accessibles depuis tous les nœuds (ex: via NFS(si cela a ete respecte comme lors de l'installation c'est que c'est ok ou Ceph).
- **Réseau** : Les nœuds doivent être sur le même sous-réseau.

#### b. Activer les Migrations Live dans Nova
```bash
sudo nano /etc/nova/nova.conf
```

```ini
[libvirt]
live_migration_flag = VIR_MIGRATE_UNDEFINE_SOURCE, VIR_MIGRATE_PEER2PEER, VIR_MIGRATE_LIVE
live_migration_uri = qemu+ssh://root@%s/system
```

#### c. Exécuter une Migration Live
```bash
openstack server migrate --live <compute-destination> <instance-id>
```

---

### **5. Vérification**
#### a. Vérifier l'Hyperviseur Xen dans OpenStack
```bash
openstack hypervisor list  # Doit afficher les compute nodes Xen
```

#### b. Créer une Instance avec Xen
```bash
openstack server create --image xen-compatible-image --flavor m1.small --network private xen-vm
```

---

### **6. Résolution des Problèmes Courants**
#### a. Erreur "No valid host found"
- Vérifiez que Nova est configuré pour Xen :
  ```bash
  nova service-list  # Doit montrer "nova-compute" comme "up"
  ```

#### b. Problèmes de Connexion XenAPI
- Vérifiez que le port **9363** est ouvert entre le controller et les compute nodes :
  ```bash
  nc -zv <IP_COMPUTE_NODE> 9363
  ```

#### c. Images Incompatibles
- Convertir les images pour Xen :
  ```bash
  qemu-img convert -O raw image.qcow2 image.raw
  openstack image create --disk-format raw --container-format bare --file image.raw xen-image
  ```

---

### **7. Documentation Officielle**
- [OpenStack XenAPI Driver](https://docs.openstack.org/nova/latest/user/xenapi.html)
- [Xen Hypervisor Configuration](https://xenproject.org/developers/guides/)

---

### **8. Notes pour Grid'5000**
- **Kadeploy** : Utilisez un environnement avec Xen préinstallé (ex: `ubuntu2204-xen`). (IMPORTANT ceci est a changer par rapport au precedent fichier)
- **Réseau** : s'Assurez que les VLANs Grid'5000 autorisent le trafic entre les nœuds.
- **Stockage** : Montez un NFS depuis le controller pour partager les images.

Cette configuration permet de remplacer KVM par Xen tout en conservant l’architecture OpenStack, avec une prise en charge complète des migrations de VMs.
