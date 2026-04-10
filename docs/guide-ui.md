# Guide UI — Créer dashboards, alertes et vues à la main

Ce guide explique comment créer manuellement chaque élément dans l'interface SigNoz sur `http://localhost:8080`.

---

## Créer un dashboard

1. Dans le menu gauche, clique sur **Dashboards**
2. Clique sur **New Dashboard**
3. Donne un nom au dashboard (ex : `Infrastructure hote`)
4. Clique sur **Add Panel** pour ajouter un premier graphique

### Configurer un panel PromQL

1. Dans le panel, choisis le type **Time Series** (graphe temporel)
2. En bas, change le mode de requête en **PromQL**
3. Colle ta requête dans le champ (ex : `100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`)
4. Règle l'axe Y si besoin (ex : `percent` pour CPU/RAM, `bytes` pour réseau/mémoire)
5. Clique sur **Run Query** pour vérifier que la courbe apparaît
6. Clique sur **Save** en haut à droite

### Requêtes PromQL disponibles

**Infrastructure hote :**

```promql
# CPU hote (%)
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memoire hote (%)
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))

# Disque hote (%)
100 * (1 - (node_filesystem_avail_bytes{fstype!=""} / node_filesystem_size_bytes{fstype!=""}))

# Reseau entrant (bytes/s)
sum by (instance) (rate(node_network_receive_bytes_total[5m]))

# Reseau sortant (bytes/s)
sum by (instance) (rate(node_network_transmit_bytes_total[5m]))
```

**Conteneurs Docker :**

```promql
# CPU par conteneur (%)
sum by (name) (rate(container_cpu_usage_seconds_total{name!=""}[5m])) * 100

# Memoire par conteneur (bytes)
sum by (name) (container_memory_usage_bytes{name!=""})

# Reseau entrant par conteneur (bytes/s)
sum by (name) (rate(container_network_receive_bytes_total{name!=""}[5m]))

# Reseau sortant par conteneur (bytes/s)
sum by (name) (rate(container_network_transmit_bytes_total{name!=""}[5m]))
```

**Application Lab :**

```promql
# Requetes par service (req/s)
sum by (service_name) (rate(lab_requests_total[5m]))

# Erreurs par service (err/s)
sum by (service_name) (rate(lab_errors_total[5m]))

# Latence p95 par service (ms)
histogram_quantile(0.95, sum by (service_name, le) (rate(lab_request_duration_ms_bucket[5m])))

# File d'attente par service
avg by (service_name) (lab_queue_depth)
```

---

## Créer une alerte

1. Dans le menu gauche, clique sur **Alerts**
2. Clique sur **New Alert Rule**
3. Choisis le type **Metric Based Alert**
4. Dans **Query**, choisis le mode **PromQL**
5. Colle ta requête PromQL
6. Dans **Condition**, règle :
   - **When** : `A` (nom de ta requête)
   - **Is** : `Above` (ou `Below`)
   - **Value** : le seuil (ex : `80` pour CPU > 80%)
7. Dans **Alert Details** :
   - **Alert Name** : nom de l'alerte
   - **Severity** : `warning` ou `critical`
   - **Evaluation Period** : `5 min`
8. Dans **Notification**, sélectionne un canal (ou configure-en un dans Settings → Alert Channels)
9. Clique sur **Save**

### Alertes recommandées

| Nom | Requête | Seuil |
|-----|---------|-------|
| CPU hote elevee | `100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` | > 80 |
| Memoire hote elevee | `100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))` | > 85 |
| Disque presque plein | `100 * (1 - (node_filesystem_avail_bytes{fstype!=""} / node_filesystem_size_bytes{fstype!=""}))` | > 90 |
| Erreurs billing-worker | `increase(lab_errors_total{service_name="billing-worker"}[5m])` | > 0 |
| Latence elevee billing-worker | `histogram_quantile(0.95, sum by (service_name, le) (rate(lab_request_duration_ms_bucket{service_name="billing-worker"}[5m])))` | > 1000 |

---

## Créer une vue sauvegardée

### Dans l'explorateur de logs

1. Dans le menu gauche, clique sur **Logs** → **Logs Explorer**
2. Applique tes filtres via les champs en haut :
   - Clique sur **Add Filter**
   - Choisis l'attribut (ex : `service.name`)
   - Choisis l'opérateur (`=`, `contains`, etc.)
   - Saisis la valeur (ex : `billing-worker`)
3. Une fois le filtre en place et les résultats visibles, clique sur l'icône **Save View** (disquette) en haut à droite
4. Donne un nom à la vue (ex : `Logs - billing-worker`)
5. La vue apparaît dans la liste déroulante **Saved Views**

### Dans l'explorateur de traces

1. Dans le menu gauche, clique sur **Traces** → **Traces Explorer**
2. Applique tes filtres (ex : `service.name = billing-worker`, ou `Status = error`)
3. Clique sur **Save View** et donne un nom

### Vues recommandées

**Logs :**

| Nom | Filtre |
|-----|--------|
| Erreurs - toutes machines | `severity_text = ERROR` |
| Logs - edge-gateway | `service.name = edge-gateway` |
| Logs - orders-api | `service.name = orders-api` |
| Logs - billing-worker | `service.name = billing-worker` |
| Requetes echouees | `body contains failed` |

**Traces :**

| Nom | Filtre |
|-----|--------|
| Traces en erreur | `Status = error` |
| Traces - billing-worker | `service.name = billing-worker` |
| Traces lentes > 500ms | `Duration > 500ms` |

---

## Configurer un canal de notification pour les alertes

1. Dans le menu gauche, clique sur **Settings** → **Alert Channels**
2. Clique sur **New Alert Channel**
3. Choisis le type :
   - **Webhook** : URL HTTP qui reçoit les alertes (ex : Slack Incoming Webhook, n8n, etc.)
   - **Email** : adresse email (nécessite un serveur SMTP configuré)
   - **Slack** : webhook Slack direct
4. Remplis les champs et clique sur **Test** pour vérifier
5. Clique sur **Save**
6. Ce canal sera sélectionnable lors de la création d'une alerte
