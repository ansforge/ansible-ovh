# 🏗️ ansible-ovh

**Plateforme d'automatisation Ansible pour l'infrastructure OVH — ANS Forge**

Ce dépôt centralise l'ensemble des playbooks, rôles et inventaires Ansible permettant le provisionnement, la configuration, le durcissement et la maintenance des machines virtuelles hébergées chez OVH (vRack), tournant sous **AlmaLinux 9 / 10**.

---

## 📑 Table des matières

- [Architecture réseau](#-architecture-réseau)
- [Prérequis](#-prérequis)
- [Installation et configuration initiale](#-installation-et-configuration-initiale)
- [Arborescence du projet](#-arborescence-du-projet)
- [Configuration Ansible](#-configuration-ansible)
- [Inventaire](#-inventaire)
- [Rôles](#-rôles)
- [Playbooks](#-playbooks)
  - [Infrastructure (plays/infra)](#-infrastructure--playsinfra)
  - [Provisionnement VM (plays/vm_provisionning)](#-provisionnement-vm--playsvm_provisionning)
  - [Patching (plays/vm_patching)](#-patching--playsvm_patching)
  - [Informations VM (plays/vm_infos)](#-informations-vm--playsvm_infos)
- [Vaults (secrets chiffrés)](#-vaults-secrets-chiffrés)
- [OpenSCAP](#-openscap)
- [Commandes de lancement](#-commandes-de-lancement)
- [Commandes de test et vérification](#-commandes-de-test-et-vérification)
- [Dépannage](#-dépannage)
- [Contribution](#-contribution)

---

## 🌐 Architecture réseau

| Machine | FQDN | IP | Réseau | Rôle |
|---|---|---|---|---|
| `infra-prod-tfansible01` | `infra-prod-tfansible01.ans.local` | `10.11.90.14` | Management | Contrôleur Ansible / Terraform |
| `infra-prod-freeipa01` | `infra-prod-freeipa01.ans.local` | `10.11.90.13` | Management | Serveur FreeIPA IDM (DNS, LDAP, Kerberos) |
| `infra-prod-repo01` | `infra-prod-repo01.ans.local` | `10.11.90.12` | Management | Serveur de dépôts AlmaLinux local |
| `infra-prod-proxy01` | `infra-prod-proxy01.ans.local` | `10.11.30.11` / `10.11.70.11` | DMZ / Proxy | Proxy Squid (2 pattes : SSH sur `eth0`, proxy sur `eth1`) |

**Réseaux :**
- `10.11.90.0/24` — Réseau management (IPA, Repo, Ansible Controller)
- `10.11.30.0/24` — Réseau DMZ / accès SSH proxy
- `10.11.70.0/24` — Réseau proxy Squid (sortie Internet contrôlée)

---

## 📋 Prérequis

- **OS** : AlmaLinux 9 ou 10
- **Ansible** : ansible-core ≥ 2.16
- **Python** : 3.9+
- **Collections requises** :
  - `freeipa.ansible_freeipa` (enrollment IPA, gestion users/groups)
- **Accès SSH** : clé SSH déployée sur toutes les machines (utilisateur `almalinux`)
- **Ansible Vault** : mot de passe vault pour les secrets FreeIPA

---

## 🚀 Installation et configuration initiale

```bash
# 1. Cloner le dépôt sur le contrôleur Ansible
git clone https://github.com/ansforge/ansible-ovh.git ~/ansible-ovh

# 2. Installer la collection FreeIPA
ansible-galaxy collection install freeipa.ansible_freeipa -p ~/ansible-ovh/collections

# 3. Vérifier la connectivité vers toutes les machines
ansible all -m ping

# 4. Vérifier la configuration
ansible --version
ansible-config dump --only-changed
```

---

## 🗂️ Arborescence du projet

```
ansible-ovh/
├── ansible.cfg                          # Configuration globale Ansible
├── .gitignore
├── inventory/
│   └── prod/
│       ├── hosts.ini                    # Inventaire principal (groupes & hôtes)
│       ├── group_vars/
│       │   ├── all/                     # Variables communes à tous les hôtes
│       │   ├── alma9/                   # Variables spécifiques AlmaLinux 9
│       │   ├── alma10/                  # Variables spécifiques AlmaLinux 10
│       │   ├── ipaservers/             # Variables serveurs FreeIPA
│       │   └── proxy/                  # Variables proxy Squid
│       └── host_vars/
│           ├── infra-prod-freeipa01.yml
│           ├── infra-prod-proxy01.yml
│           ├── infra-prod-repo01.yml
│           └── infra-prod-tfansible01.yml
├── plays/
│   ├── infra/                          # Playbooks déploiement infrastructure
│   ├── vm_provisionning/              # Playbooks provisionnement VMs
│   ├── vm_patching/                   # Playbooks mise à jour / patching
│   └── vm_infos/                      # Playbooks collecte d'informations
├── roles/
│   ├── role_chrony/                   # Configuration NTP Chrony
│   ├── role_copy_ssh_key/            # Déploiement clés SSH
│   ├── role_hardening_openscap/      # Durcissement CIS via OpenSCAP
│   ├── role_installation_openscap/   # Installation OpenSCAP
│   ├── role_ipa/                      # Opérations FreeIPA (enrollment, etc.)
│   ├── role_remediation_openscap/    # Remédiation OpenSCAP
│   ├── role_resolvconf/              # Configuration DNS resolv.conf
│   ├── role_setup_freeipa_client/    # Configuration client FreeIPA
│   ├── role_setup_freeipa_server/    # Déploiement serveur FreeIPA IDM
│   ├── role_setup_proxy_server/      # Installation/config Squid
│   ├── role_setup_proxy_whitelist/   # Gestion whitelist Squid
│   ├── role_setup_repo_client/       # Configuration client repo local
│   ├── role_setup_repo_server/       # Déploiement serveur de dépôts
│   ├── role_tfansible/               # Configuration contrôleur Terraform/Ansible
│   └── role_toolbox/                 # Installation outils système (EPEL + utilitaires)
├── vaults/
│   └── vault_freeipa.yml             # Secrets FreeIPA chiffrés (Ansible Vault)
├─�� openscap-ansible/
│   └── openscap-ansible.zip          # Playbooks OpenSCAP pré-packagés
├── collections/                       # Collections Ansible (freeipa, etc.)
└── plugins/
    └── actions/                       # Plugins d'action custom (manage_lockfile, manage_inifile)
```

---

## ⚙️ Configuration Ansible

Fichier `ansible.cfg` :

```ini
[defaults]
remote_user = almalinux
inventory = ~/ansible-ovh/inventory/prod/hosts.ini
roles_path = ~/ansible-ovh/roles
collections_path = ~/ansible-ovh/collections
action_plugins = ~/ansible-ovh/plugins/actions
deprecation_warnings = false
retry_files_enabled = false
host_key_checking = False
```

| Paramètre | Valeur | Description |
|---|---|---|
| `remote_user` | `almalinux` | Utilisateur SSH par défaut |
| `inventory` | `inventory/prod/hosts.ini` | Inventaire de production |
| `roles_path` | `roles/` | Chemin des rôles |
| `collections_path` | `collections/` | Chemin des collections (FreeIPA) |
| `action_plugins` | `plugins/actions/` | Plugins custom (lockfile, inifile) |
| `host_key_checking` | `False` | Désactive la vérification des clés SSH hôtes |

---

## 📦 Inventaire

### Groupes définis dans `hosts.ini`

| Groupe | Membres | Usage |
|---|---|---|
| `alma10` | repo01, tfansible01, freeipa01, proxy01 | Toutes les machines AlmaLinux 10 |
| `infra_prod` | repo01, tfansible01, freeipa01, proxy01 | Ensemble de l'infrastructure prod |
| `cmf` | repo01, tfansible01, freeipa01, proxy01 | Groupe CMF (Configuration Management Framework) |
| `ipaservers` | freeipa01 | Serveurs FreeIPA uniquement |
| `tfansible` | tfansible01 | Contrôleur Terraform/Ansible |
| `repo` | repo01 | Serveur de dépôts |
| `proxy` | proxy01 | Serveur proxy Squid |

### Variables hôtes (`host_vars`)

Chaque hôte possède un fichier YAML avec au minimum :

```yaml
ansible_host: 10.11.90.12        # IP de connexion SSH
fqdn: infra-prod-repo01.ans.local # FQDN complet
```

Le proxy a une variable supplémentaire :

```yaml
proxy_listen_ip: 10.11.70.11     # IP d'écoute Squid (2ème interface)
```

### Variables de groupe (`group_vars`)

| Dossier | Contenu |
|---|---|
| `all/` | Variables globales (domaine, NTP, DNS, etc.) |
| `alma9/` | Repos et config spécifiques AlmaLinux 9 |
| `alma10/` | Repos et config spécifiques AlmaLinux 10 |
| `ipaservers/` | Config serveur FreeIPA (realm, domain, etc.) |
| `proxy/` | Config proxy Squid |

---

## 🎭 Rôles

### Rôles d'infrastructure

| Rôle | Description |
|---|---|
| `role_setup_freeipa_server` | Déploie et configure le serveur FreeIPA IDM (DNS, LDAP, Kerberos, certificats). Cible : `ipaservers` |
| `role_setup_freeipa_client` | Configure un client FreeIPA : télécharge le CA, prépare les prérequis, puis enroll via `freeipa.ansible_freeipa.ipaclient` |
| `role_ipa` | Rôle générique pour les opérations IPA (enrollment client, etc.) via le paramètre `ipa_operation` |
| `role_setup_repo_server` | Configure le serveur de dépôts AlmaLinux local (httpd + repos miroir). Cible : `repo` |
| `role_setup_repo_client` | Configure les clients pour utiliser le repo local (désactive les repos publics, configure les repos locaux en HTTPS) |
| `role_setup_proxy_server` | Installe et configure Squid en mode proxy explicite. Cible : `squid_servers` |
| `role_setup_proxy_whitelist` | Met à jour la whitelist de domaines autorisés sur le proxy Squid |
| `role_tfansible` | Configure le serveur contrôleur Terraform/Ansible (outils, config). Cible : `tfansible` |

### Rôles de provisionnement

| Rôle | Description |
|---|---|
| `role_chrony` | Configure le client NTP Chrony sur les machines cibles |
| `role_resolvconf` | Configure le fichier `/etc/resolv.conf` (DNS vers FreeIPA) |
| `role_copy_ssh_key` | Déploie les clés SSH publiques sur les serveurs cibles |
| `role_toolbox` | Active le dépôt EPEL et installe les outils système de base |

### Rôles de sécurité (OpenSCAP)

| Rôle | Description |
|---|---|
| `role_installation_openscap` | Installe les outils OpenSCAP et les guides SCAP sur AlmaLinux |
| `role_hardening_openscap` | Applique le profil de durcissement CIS Server Level 1 via OpenSCAP |
| `role_remediation_openscap` | Applique les remédiations automatiques OpenSCAP selon le profil CIS |

---

## 📖 Playbooks

### 🏭 Infrastructure — `plays/infra/`

| Playbook | Description | Commande |
|---|---|---|
| `play_freeipa_server_deploy.yml` | Déploie le serveur FreeIPA IDM | `ansible-playbook plays/infra/play_freeipa_server_deploy.yml --ask-vault-pass` |
| `play_freeipa_data_integrate.yml` | Intègre les données dans FreeIPA (utilisateurs, groupes) | `ansible-playbook plays/infra/play_freeipa_data_integrate.yml --ask-vault-pass` |
| `play_repo_server_deploy.yml` | Déploie le serveur de dépôts local | `ansible-playbook plays/infra/play_repo_server_deploy.yml` |
| `play_proxy_deploy.yml` | Déploie le proxy Squid | `ansible-playbook plays/infra/play_proxy_deploy.yml` |
| `play_proxy_whitelist.yml` | Met à jour la whitelist Squid | `ansible-playbook plays/infra/play_proxy_whitelist.yml` |
| `play_terraform_controller_deploy.yml` | Configure le contrôleur Terraform/Ansible | `ansible-playbook plays/infra/play_terraform_controller_deploy.yml` |
| `play_jump_deploy.yml` | Configure le serveur rebond SSH (fail2ban, sécurisation) | `ansible-playbook plays/infra/play_jump_deploy.yml` |

### 🖥️ Provisionnement VM — `plays/vm_provisionning/`

> **Note** : Les playbooks avec `{{ HOSTS }}` nécessitent le paramètre `-e "HOSTS=<groupe_ou_host>"`

| Playbook | Description | Commande |
|---|---|---|
| `play_inv_add_host.yml` | Ajoute un hôte dans l'inventaire (avec lock) | `ansible-playbook plays/vm_provisionning/play_inv_add_host.yml -e "vm_name=<nom> vm_ip=<ip> vm_env=<env>"` |
| `play_inv_remove_host.yml` | Supprime un hôte de l'inventaire | `ansible-playbook plays/vm_provisionning/play_inv_remove_host.yml -e "vm_name=<nom>"` |
| `play_lin_repo_client_deploy.yml` | Configure les repos locaux sur les VMs | `ansible-playbook plays/vm_provisionning/play_lin_repo_client_deploy.yml -e "HOSTS=alma10"` |
| `play_lin_resolvconf_deploy.yml` | Configure le DNS (resolv.conf) | `ansible-playbook plays/vm_provisionning/play_lin_resolvconf_deploy.yml -e "HOSTS=infra_prod"` |
| `play_lin_chrony_client_deploy.yml` | Configure le NTP (Chrony) | `ansible-playbook plays/vm_provisionning/play_lin_chrony_client_deploy.yml -e "HOSTS=infra_prod"` |
| `play_lin_ssh_key_deploy.yml` | Déploie les clés SSH | `ansible-playbook plays/vm_provisionning/play_lin_ssh_key_deploy.yml -e "HOSTS=infra_prod"` |
| `play_lin_toolbox_deploy.yml` | Installe les outils système | `ansible-playbook plays/vm_provisionning/play_lin_toolbox_deploy.yml` |
| `play_lin_ipaclient_enroll.yml` | Enrôle les machines dans FreeIPA | `ansible-playbook plays/vm_provisionning/play_lin_ipaclient_enroll.yml -e "HOSTS=infra_prod" --ask-vault-pass` |
| `play_lin_fix_netaddr.yml` | Fige l'IP/MAC en configuration réseau statique | `ansible-playbook plays/vm_provisionning/play_lin_fix_netaddr.yml -e "HOSTS=infra_prod"` |
| `play_installation_openscap.yml` | Installe OpenSCAP | `ansible-playbook plays/vm_provisionning/play_installation_openscap.yml -e "HOSTS=infra_prod"` |
| `play_hardening_openscap.yml` | Applique le durcissement CIS L1 | `ansible-playbook plays/vm_provisionning/play_hardening_openscap.yml -e "HOSTS=infra_prod"` |
| `play_remediation_openscap.yml` | Applique les remédiations OpenSCAP | `ansible-playbook plays/vm_provisionning/play_remediation_openscap.yml -e "HOSTS=infra_prod"` |

### 🔄 Patching — `plays/vm_patching/`

| Playbook | Description | Commande |
|---|---|---|
| `play_lin_update.yml` | Met à jour tous les paquets et le kernel, avec gestion du reboot | `ansible-playbook plays/vm_patching/play_lin_update.yml -e "HOSTS=alma10"` |

**Fonctionnement du patching :**
1. Détecte la version AlmaLinux (9 ou 10) et active les repos locaux correspondants
2. Applique `yum update` sur tous les paquets
3. Vérifie si un reboot est nécessaire via `needs-restarting -r`
4. Reboot automatiquement si nécessaire
5. Stocke les logs de mise à jour dans `plays/vm_patching/update_results/`
6. Génère des rapports dans `plays/vm_patching/reports/`

**Tags disponibles :**
```bash
# Mise à jour uniquement (sans reboot)
ansible-playbook plays/vm_patching/play_lin_update.yml -e "HOSTS=alma10" --tags update_only

# Reboot uniquement
ansible-playbook plays/vm_patching/play_lin_update.yml -e "HOSTS=alma10" --tags reboot

# Historique yum uniquement
ansible-playbook plays/vm_patching/play_lin_update.yml -e "HOSTS=alma10" --tags yum_history_only
```

### ℹ️ Informations VM — `plays/vm_infos/`

| Playbook | Description | Commande |
|---|---|---|
| `play_lin_get_failed_services.yml` | Liste les services systemd en état `failed` sur les hôtes cibles | `ansible-playbook plays/vm_infos/play_lin_get_failed_services.yml -e "HOSTS=infra_prod"` |

---

## 🔒 Vaults (secrets chiffrés)

Les secrets sont stockés dans `vaults/vault_freeipa.yml`, chiffré avec **Ansible Vault**.

**Variables contenues :**
- `vault_ipaadmin_password` — Mot de passe admin FreeIPA
- Autres credentials IPA

**Gestion du vault :**

```bash
# Éditer les secrets
ansible-vault edit vaults/vault_freeipa.yml

# Afficher les secrets (déchiffré)
ansible-vault view vaults/vault_freeipa.yml

# Changer le mot de passe du vault
ansible-vault rekey vaults/vault_freeipa.yml
```

> ⚠️ **Ne jamais commiter le mot de passe vault en clair.** Utiliser `--ask-vault-pass` ou un fichier vault password.

---

## 🛡️ OpenSCAP

Le durcissement des machines suit le profil **CIS Server Level 1** (`xccdf_org.ssgproject.content_profile_cis_server_l1`).

**Workflow complet de durcissement :**

```bash
# 1. Installer les outils OpenSCAP
ansible-playbook plays/vm_provisionning/play_installation_openscap.yml -e "HOSTS=infra_prod"

# 2. Appliquer le hardening CIS L1
ansible-playbook plays/vm_provisionning/play_hardening_openscap.yml -e "HOSTS=infra_prod"

# 3. Appliquer les remédiations
ansible-playbook plays/vm_provisionning/play_remediation_openscap.yml -e "HOSTS=infra_prod"
```

Le dossier `openscap-ansible/` contient un archive ZIP avec des playbooks OpenSCAP pré-packagés.

---

## 🚀 Commandes de lancement

### Ordre de provisionnement complet d'une nouvelle VM

```bash
# 1. Ajouter la VM dans l'inventaire
ansible-playbook plays/vm_provisionning/play_inv_add_host.yml \
  -e "vm_name=infra-prod-newvm01 vm_ip=10.11.90.20 vm_env=infra_prod"

# 2. Déployer les clés SSH
ansible-playbook plays/vm_provisionning/play_lin_ssh_key_deploy.yml \
  -e "HOSTS=infra-prod-newvm01"

# 3. Configurer le DNS
ansible-playbook plays/vm_provisionning/play_lin_resolvconf_deploy.yml \
  -e "HOSTS=infra-prod-newvm01"

# 4. Configurer les repos locaux
ansible-playbook plays/vm_provisionning/play_lin_repo_client_deploy.yml \
  -e "HOSTS=alma10"

# 5. Installer les outils de base
ansible-playbook plays/vm_provisionning/play_lin_toolbox_deploy.yml

# 6. Configurer NTP
ansible-playbook plays/vm_provisionning/play_lin_chrony_client_deploy.yml \
  -e "HOSTS=infra-prod-newvm01"

# 7. Enrôler dans FreeIPA
ansible-playbook plays/vm_provisionning/play_lin_ipaclient_enroll.yml \
  -e "HOSTS=infra-prod-newvm01" --ask-vault-pass

# 8. Figer la configuration réseau en statique
ansible-playbook plays/vm_provisionning/play_lin_fix_netaddr.yml \
  -e "HOSTS=infra-prod-newvm01"

# 9. Installer et appliquer le hardening OpenSCAP
ansible-playbook plays/vm_provisionning/play_installation_openscap.yml \
  -e "HOSTS=infra-prod-newvm01"
ansible-playbook plays/vm_provisionning/play_hardening_openscap.yml \
  -e "HOSTS=infra-prod-newvm01"
ansible-playbook plays/vm_provisionning/play_remediation_openscap.yml \
  -e "HOSTS=infra-prod-newvm01"

# 10. Appliquer les mises à jour
ansible-playbook plays/vm_patching/play_lin_update.yml \
  -e "HOSTS=infra-prod-newvm01"
```

### Ciblage des hôtes

```bash
# Un seul hôte
-e "HOSTS=infra-prod-repo01"

# Un groupe entier
-e "HOSTS=alma10"
-e "HOSTS=infra_prod"

# Plusieurs hôtes
-e "HOSTS=infra-prod-repo01,infra-prod-tfansible01"

# Limiter l'exécution (en plus du groupe)
-e "HOSTS=infra_prod" --limit infra-prod-repo01
```

---

## 🧪 Commandes de test et vérification

```bash
# Tester la connectivité SSH vers tous les hôtes
ansible all -m ping

# Tester un groupe spécifique
ansible alma10 -m ping

# Tester un hôte spécifique
ansible infra-prod-repo01 -m ping

# Mode dry-run (check) — simule sans appliquer
ansible-playbook plays/vm_provisionning/play_lin_repo_client_deploy.yml \
  -e "HOSTS=alma10" --check

# Mode verbose (debug)
ansible-playbook plays/vm_provisionning/play_lin_repo_client_deploy.yml \
  -e "HOSTS=alma10" -vvv

# Mode diff (affiche les changements)
ansible-playbook plays/vm_provisionning/play_lin_repo_client_deploy.yml \
  -e "HOSTS=alma10" --diff

# Lister les hôtes ciblés sans exécuter
ansible-playbook plays/vm_provisionning/play_lin_repo_client_deploy.yml \
  -e "HOSTS=alma10" --list-hosts

# Lister les tâches d'un playbook
ansible-playbook plays/vm_provisionning/play_lin_repo_client_deploy.yml \
  -e "HOSTS=alma10" --list-tasks

# Vérifier la syntaxe d'un playbook
ansible-playbook plays/vm_provisionning/play_lin_repo_client_deploy.yml \
  -e "HOSTS=alma10" --syntax-check

# Collecter les facts d'un hôte
ansible infra-prod-repo01 -m setup

# Vérifier les services en échec
ansible-playbook plays/vm_infos/play_lin_get_failed_services.yml \
  -e "HOSTS=infra_prod"

# Exécuter une commande ad-hoc sur un groupe
ansible infra_prod -m shell -a "cat /etc/resolv.conf" -b
ansible infra_prod -m shell -a "systemctl status chronyd" -b
```

---

## 🔧 Dépannage

### Problèmes courants

| Problème | Cause probable | Solution |
|---|---|---|
| `Failed to verify IPA Server` | DNS ne résout pas le serveur IPA | Vérifier `/etc/resolv.conf` et `/etc/hosts` sur la cible |
| `curl: (28) Timeout port 443` | Firewall ou routage réseau | Vérifier `firewall-cmd --list-all` sur le serveur IPA, ouvrir `http`/`https` |
| `Host unreachable` | Clé SSH non déployée ou mauvaise IP | Vérifier `host_vars/<host>.yml` et le déploiement SSH |
| Repo DNF échoue | Repos locaux mal configurés | Relancer `play_lin_repo_client_deploy.yml` |
| `Permission denied` | `become: yes` manquant | Vérifier que le playbook utilise `become: true` |

### Commandes de diagnostic

```bash
# Depuis le contrôleur Ansible
ssh almalinux@<IP> "cat /etc/resolv.conf"
ssh almalinux@<IP> "sudo firewall-cmd --list-all"
ssh almalinux@<IP> "sudo ss -tlnp | grep -E ':443|:80'"
ssh almalinux@<IP> "curl -kL --connect-timeout 5 https://10.11.90.13/ipa/config/ca.crt"
ssh almalinux@<IP> "ip route show"
```

---

## 🤝 Contribution

1. Créer une branche depuis `amont` :
   ```bash
   git checkout -b feature/ma-feature amont
   ```
2. Tester en mode `--check` avant de commiter
3. Commiter et pousser
4. Créer une Pull Request vers `amont`

### Conventions

- **Nommage des rôles** : `role_<fonction>` (ex: `role_setup_freeipa_server`)
- **Nommage des playbooks** : `play_<scope>_<action>.yml` (ex: `play_lin_repo_client_deploy.yml`)
- **Nommage des hôtes** : `infra-<env>-<service><num>` (ex: `infra-prod-freeipa01`)
- **Branche par défaut** : `amont`

---

## 📄 Licence

*Non spécifiée — Consulter l'organisation [ANS Forge](https://github.com/ansforge) pour plus d'informations.*

---

> **Maintenu par l'équipe Infrastructure ANS Forge** — Automatisation OVH vRack avec Ansible
