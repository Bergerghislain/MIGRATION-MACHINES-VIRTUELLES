INSTALLATION D' OPENSTACK VIA DEVSTACK SUR LE CONTROLLER ET LES NOEUDS DE CALCUL PRESENT SUR GRID5000:


###1-connexion a une machine de grid5000
####a) entrer ses identifiants:  ssh betheubo@access.grid5000.fr

####b) se connecter a un site precis : ssh nantes

####c) faire une requete pour reserver les machines d' un noeud :

si je veux une machine complete et pas exotique  ( prendre une machine non exotique car , une machine complete nous permet d' avoir plus de droits et dans la suite nous permettra de pouvoir decider de la migration de la VM)

oarsub -t deploy -p econome -l /switch=1/nodes=3,walltime=7:00:00 "sleep 7h"

ATTENTION: Une possibilite est que tous les noeuds ne sont pas disponibles et du coup on fait plusieurs reservations en separant bien le noeud de control et celui de calcul mais ces derniers doivent etre sur le meme site, on fait comme suit :

```bash
# Controller Node
oarsub -t deploy -p dahu -l /nodes=1,walltime=6:00:00 -n "openstack-ctl" "sleep 6h"

# Compute Nodes (ex: 2 nœuds)
oarsub -t deploy -p dahu -l /nodes=2,walltime=6:00:00 -n "openstack-compute" "sleep 6h"
```


####e)Se connecter au job OAR : oarsub -C JOBID ( a voir dans le terminal)

####f) je deploie l' OS sur tous les nœuds réservés:

-kadeploy3 -e ubuntu2204-nfs ( version compatible avec devstack)
-kadeploy3 debian11-min ( n' utiliser que si la premiere commmande n'a pas marche) mais cette version d'ubuntu pose souvent des problemes car problemes de compatibilite avec devstack.

####g) se connecter a un noeud : ssh root@econome-5 ( econome-5 ici est le nom d'un des noeuds reserves qui me servira de controller)
			   : ssh root@econome-9 ( econome-9 ici est le nom d'un des noeuds reserves qui me servira de noeuds de compute)

###2) installation des paquets necessaires sur tous les noeuds

apt-get update
apt-get install sudo

###3) installation des librairies necessaires sur tous les noeuds
sudo apt update
sudo apt install -y git python3 python3-pip

sudo apt update
sudo apt install iptables
sudo iptables --version

###4)COMMANDES PROPRES AU NOEUD DE CONTROLLER:

####a)  Installation de MariaDB ( executer une a une les commandes suivantes )

sudo apt purge mariadb-* -y
sudo rm -rf /etc/mysql /var/lib/mysql
sudo apt install mariadb-server python3-pymysql --reinstall -y

# Configuration critique
sudo nano /etc/mysql/mariadb.conf.d/99-openstack.cnf

Dans le fichier 99-openstack.cnf cree on y mets le contenu suivant :

[mysqld]
bind-address = 0.0.0.0
default-storage-engine = innodb
innodb_file_per_table = on
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8
default-authentication-plugin = mysql_native_password  # Évite les erreurs d'authentification
skip-name-resolve  # Ignore la résolution DNS
innodb_flush_method = O_DIRECT

####b)Sécurisation de MariaDB

sudo systemctl restart mariadb
sudo mysql_secure_installation  # Répondez "Y" à tout sauf pour le mot de passe root (laissez vide si non demandé)

#### c. Création des Bases de Données
```bash
mysql -u root <<EOF
CREATE DATABASE glance;
CREATE DATABASE nova_api;
CREATE DATABASE nova;
CREATE DATABASE nova_cell0;
CREATE DATABASE placement;
CREATE DATABASE neutron;

GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON placement.* TO 'placement'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY 'admin';
FLUSH PRIVILEGES;
EOF
```

#### d. Installation de DevStack
ATTENTION: les machines que je servais etaient toutes dans un sous reseau bien precis( "192.168.100.0/24") si le votre differe se rassurer de sa valeur avant de modifier le fichier local.conf, aussi d'une machine a une autre la publique interface peut changer pour se rassurer faire un ip a dans le terminal et editer le fichier local.conf en consequence.

```bash
git clone https://opendev.org/openstack/devstack.git /opt/devstack
sudo /opt/devstack/tools/create-stack-user.sh
sudo chown -R stack:stack /opt/devstack

# Fichier de configuration
cat > /opt/devstack/local.conf <<EOF
[[local|localrc]]
HOST_IP=$(hostname -I | awk '{print $1}')
SERVICE_HOST=\$HOST_IP

# Activer les services
ENABLED_SERVICES=key,mysql,rabbitmq,n-api,n-crt,n-obj,n-sch,n-cauth,placement-api,horizon,neutron

# Désactiver les services inutiles
disable_service tempest heat cinder

# Mots de passe
ADMIN_PASSWORD=admin
DATABASE_PASSWORD=admin
RABBIT_PASSWORD=admin
SERVICE_PASSWORD=admin

# Configuration Neutron (réseau)
Q_USE_SECGROUP=True
FLOATING_RANGE="192.168.100.0/24"   		#propre aux noeuds reserves
PUBLIC_NETWORK_GATEWAY="192.168.100.1" 		#propre aux noeuds reserves
PUBLIC_INTERFACE=eth0				#propre aux noeuds reserves
EOF

# Lancer l'installation
su - stack
cd /opt/devstack
./stack.sh
```

---
La suite des commandes ne concernent que les noeuds de calcul

### **3. Configuration des Compute Nodes**
#### a. Préparation de Base
```bash
sudo apt update
sudo apt install -y git python3 python3-pip
```

#### b. Configuration DevStack
```bash
git clone https://opendev.org/openstack/devstack.git /opt/devstack
sudo /opt/devstack/tools/create-stack-user.sh
sudo chown -R stack:stack /opt/devstack

cat > /opt/devstack/local.conf <<EOF
[[local|localrc]]
HOST_IP=$(hostname -I | awk '{print $1}')
SERVICE_HOST=<IP_CONTROLLER>  # Remplacer par l'IP du controller

# Activer uniquement les services compute
ENABLED_SERVICES=n-cpu,neutron

# Désactiver les services inutiles
disable_service n-api n-sch n-cauth horizon

# Configuration Nova
NOVA_VNC_ENABLED=True
NOVNCPROXY_URL="http://\$SERVICE_HOST:6080/vnc_auto.html"

# Configuration Neutron
Q_USE_SECGROUP=True
EOF

# Lancer l'installation
su - stack
cd /opt/devstack
./stack.sh
```

---
Apres tout cela on verifie L'installation par:

### **4. Vérifications Post-Installation**
#### a. Sur le Controller
```bash
openstack compute service list  # Doit lister tous les compute nodes
openstack network agent list    # Doit montrer les agents Neutron actifs
```

#### b. Sur les Compute Nodes
```bash
systemctl status nova-compute neutron-linuxbridge-agent
```

#### c. Accès à Horizon ( ceci est a implementer on arrive a avoir une interface visuelle sur grid 5000 ce qui nest pas possible a ma connaisance )
- URL : `http://<IP_CONTROLLER>/dashboard`
- Identifiants : `admin` / `admin`

---

### **5. Résolution des Problèmes Courants(S' il y'en a)**
#### a. **MariaDB "Access Denied"**
```bash
sudo mysql -u root -padmin -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'admin'; FLUSH PRIVILEGES;"
```

#### b. **Service MySQL Ne Démarre Pas**
```bash
sudo systemctl unmask mariadb
sudo chown -R mysql:mysql /var/lib/mysql
sudo systemctl restart mariadb
```

#### c. **Erreur "No Valid Host" dans Nova**
```bash
# Vérifier que les compute nodes sont enregistrés
openstack compute service list
# Si vide, redémarrer Nova sur les compute nodes
sudo systemctl restart nova-compute
```

#### d. **Problèmes de Réseau avec Neutron**
```bash
# Recréer les réseaux par défaut
openstack network create --share --external --provider-physical-network public --provider-network-type flat public
openstack subnet create --network public --allocation-pool start=192.168.100.100,end=192.168.100.200 --gateway 192.168.100.1 --subnet-range 192.168.100.0/24 public-subnet
```


### **7. Bonnes Pratiques**
- **Sauvegardes** : 
  ```bash
  mysqldump -u root -padmin --all-databases > openstack-backup.sql
  ```
- **Monitoring** :
  ```bash
  sudo apt install prometheus-node-exporter  # Sur tous les nœuds
  ```
- **Mises à Jour** :
  ```bash
  cd /opt/devstack && git pull origin master
  ```

Ce guide intègre toutes les corrections pour les erreurs spécifiques à Grid'5000 (problèmes MariaDB, réseau, services) et garantit une installation stable. Pour des cas spécifiques non couverts, consultez les logs dans `/opt/stack/logs/`.
