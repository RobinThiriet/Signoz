# Dashboards et alertes

Ce document te donne une base simple pour afficher l'infrastructure et creer des alertes utiles dans SigNoz.

## Ce qui remonte dans la stack

La stack principale collecte :

- CPU hote
- memoire hote
- disque hote
- reseau hote
- metriques des conteneurs Docker

## Activer la supervision infrastructure

La supervision CPU/RAM/disque/reseau et conteneurs est incluse dans `compose.yaml`.

```bash
cd /root/Signoz
docker compose up -d
```

## Dashboards a creer dans SigNoz

1. ouvre `http://localhost:8080`
2. connecte-toi
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

Requetes PromQL :

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

Requetes PromQL :

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

## Dashboard 3 - Application Lab

Panels recommandes :

- total de requetes par service
- total d'erreurs par service
- latence p95 par service
- profondeur de file d'attente

Requetes PromQL :

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

Note : si les labels apparaissent sous la forme `service.name` (avec un point) plutot que `service_name`, ajuste le filtre en consequence.

## Alertes recommandees

Chaque alerte est basee sur une requete PromQL. Cree-les dans SigNoz via `Alerts` → `New Alert Rule` → mode PromQL.

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

## Alerte 4 - Erreurs billing-worker

- nom : `Erreurs billing-worker`
- requete :

```promql
increase(lab_errors_total{service_name="billing-worker"}[5m])
```

- condition : declencher si la valeur est `> 0`
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
5. utilise les requetes ci-dessus en mode PromQL
6. pour les alertes sur des compteurs, prefere `increase(...[5m])` plutot qu'une valeur brute

## Ce que tu dois presenter

- dashboard infrastructure hote
- dashboard conteneurs Docker
- dashboard applicatif du lab
- une alerte sur `billing-worker`
