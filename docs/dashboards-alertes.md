# Dashboards et alertes

Ce document te donne une base simple pour afficher l'infrastructure et creer des alertes utiles dans SigNoz.

## Ce qui remonte apres cette mise a jour

La stack principale collecte maintenant :

- CPU hote
- memoire hote
- disque hote
- reseau hote
- metriques des conteneurs Docker

Si tu actives la pile GPU NVIDIA, tu pourras aussi suivre :

- utilisation GPU
- memoire GPU
- temperature GPU

Important :

- le CPU, la memoire, le disque, le reseau et les conteneurs remontent deja avec `compose.yaml`
- le GPU ne remonte que si la machine a un GPU NVIDIA compatible et si `compose.gpu.yaml` est lance
- si tu ne vois aucune metrique `DCGM_*`, c'est normal tant que l'exporter GPU n'est pas actif

## Activer la supervision infrastructure

La supervision CPU/RAM/disque/reseau et conteneurs est incluse dans `compose.yaml`.

Redemarrage conseille :

```bash
cd /root/Signoz
docker compose up -d
```

## Activer la supervision GPU

La supervision GPU est optionnelle et demande un hote avec GPU NVIDIA et le runtime Docker NVIDIA.

Demarrage :

```bash
cd /root/Signoz
docker compose -f compose.yaml -f compose.gpu.yaml up -d
```

Si tu n'as pas de GPU NVIDIA, tu peux ignorer cette partie.

## Dashboards a creer dans SigNoz

Dans SigNoz :

1. ouvre `http://localhost:8080`
2. connecte-toi avec le compte cree au premier lancement
3. ouvre `Dashboards`
4. cree un nouveau dashboard
5. ajoute un panel par requete ci-dessous

## Dashboard 1 - Infrastructure hote

Panels recommandes :

- CPU hote
- memoire hote
- espace disque
- trafic reseau entrant
- trafic reseau sortant

Requetes PromQL utiles :

```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

```promql
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))
```

```promql
100 * (1 - (node_filesystem_avail_bytes{fstype!=""} / node_filesystem_size_bytes{fstype!=""}))
```

```promql
sum by (instance) (rate(node_network_receive_bytes_total[5m]))
```

```promql
sum by (instance) (rate(node_network_transmit_bytes_total[5m]))
```

## Dashboard 2 - Conteneurs Docker

Panels recommandes :

- CPU par conteneur
- memoire par conteneur
- trafic reseau par conteneur

Requetes utiles :

```promql
sum by (name) (rate(container_cpu_usage_seconds_total{name!=""}[5m])) * 100
```

```promql
sum by (name) (container_memory_usage_bytes{name!=""})
```

```promql
sum by (name) (rate(container_network_receive_bytes_total{name!=""}[5m]))
```

```promql
sum by (name) (rate(container_network_transmit_bytes_total{name!=""}[5m]))
```

## Dashboard 3 - GPU NVIDIA

Seulement si `compose.gpu.yaml` est actif.

Panels recommandes :

- utilisation GPU
- memoire GPU utilisee
- temperature GPU

Requetes utiles :

```promql
DCGM_FI_DEV_GPU_UTIL
```

```promql
DCGM_FI_DEV_FB_USED
```

```promql
DCGM_FI_DEV_GPU_TEMP
```

## Dashboard 4 - Application Lab

Panels recommandes :

- total de requetes par service
- total d'erreurs par service
- latence moyenne par service
- profondeur de file d'attente

Requetes utiles :

```promql
sum by (service_name) (rate(lab_requests_total[5m]))
```

```promql
sum by (service_name) (rate(lab_errors_total[5m]))
```

```promql
histogram_quantile(0.95, sum by (service_name, le) (rate(lab_request_duration_ms_bucket[5m])))
```

```promql
avg by (service_name) (lab_queue_depth)
```

Note : si les labels apparaissent sous la forme `service.name` (avec un point) plutot que `service_name` dans ton interface, ajuste le filtre en consequence.

## Alertes recommandees

## Alerte 1 - CPU hote elevee

- nom : `CPU hote elevee`
- requete :

```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

- condition : declencher si la valeur est `> 80`

## Alerte 2 - Memoire hote elevee

- nom : `Memoire hote elevee`
- requete :

```promql
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))
```

- condition : declencher si la valeur est `> 85`

## Alerte 3 - Disque presque plein

- nom : `Disque presque plein`
- requete :

```promql
100 * (1 - (node_filesystem_avail_bytes{fstype!=""} / node_filesystem_size_bytes{fstype!=""}))
```

- condition : declencher si la valeur est `> 90`

## Alerte 4 - Erreurs du lab

- nom : `Erreurs billing-worker`
- requete :

```promql
increase(lab_errors_total{service_name="billing-worker"}[5m])
```

Si le filtre `service_name` n'apparait pas tel quel dans ton interface, recree l'alerte en filtrant sur le label `service.name` dans l'UI.

Condition conseillee :

- declencher si la valeur est `> 0`
- evaluation sur les `5` dernieres minutes

## Alerte 5 - Latence elevee billing-worker

- nom : `Latence elevee billing-worker`
- requete :

```promql
histogram_quantile(0.95, sum by (service_name, le) (rate(lab_request_duration_ms_bucket{service_name="billing-worker"}[5m])))
```

- condition : declencher si la valeur est `> 1000` (1 seconde)

## Comment les creer dans l'interface

1. ouvre `http://localhost:8080`
2. connecte-toi
3. ouvre `Dashboards` pour les vues
4. ouvre `Alertes` pour les regles
5. utilise les requetes ci-dessus en mode PromQL ou metric query selon l'ecran
6. pour les alertes basees sur des compteurs, prefere `increase(...[5m])` plutot qu'une valeur brute

## Pourquoi tu ne voyais pas le CPU ou le GPU

Avant cette mise a jour, la stack de demo remontait surtout les signaux applicatifs :

- traces
- logs
- metriques custom du lab

Maintenant, elle remonte aussi les metriques d'infrastructure via :

- `node-exporter` pour l'hote
- `cadvisor` pour les conteneurs Docker
- `dcgm-exporter` en option pour le GPU NVIDIA

Concretement :

- si tu cherches `node_`, tu trouveras les metriques hote
- si tu cherches `container_`, tu trouveras les metriques Docker
- si tu cherches `DCGM_`, tu trouveras les metriques GPU uniquement si l'extension GPU est active

## Ce que tu dois presenter

- dashboard infrastructure hote
- dashboard conteneurs Docker
- dashboard applicatif du lab
- une alerte sur `billing-worker`
- si GPU present : une vue GPU
