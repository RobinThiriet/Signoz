# Installation locale de SigNoz

Cette installation se lance directement depuis `/root/Signoz`.

## Demarrage

```bash
cd /root/Signoz
docker compose up -d
```

## Arret

```bash
cd /root/Signoz
docker compose down
```

## Acces

- interface SigNoz : http://localhost:8080
- OTLP gRPC : `localhost:4317`
- OTLP HTTP : `http://localhost:4318`

## Premiere connexion

Il n'y a pas d'identifiants predefinis.

Au premier acces sur `http://localhost:8080`, tu dois :

1. creer le compte administrateur
2. choisir ton email
3. choisir ton mot de passe

Ce seront ensuite tes identifiants de connexion.

## Verification rapide

```bash
cd /root/Signoz
docker compose ps
curl http://localhost:8080/api/v1/health
```

## Connecter une autre application

### Application sur la machine hote

```bash
export OTEL_SERVICE_NAME=mon-application
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
```

### Application dans Docker

Si elle partage le reseau `signoz-net` :

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://signoz-otel-collector:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
```

## Lab de test 3 machines

La stack de test avec trois machines simulees est documentee ici :

- `/root/Signoz/docs/signoz-lab.md`
- `/root/Signoz/docs/dashboards-alertes.md`

Demarrage :

```bash
cd /root/Signoz
docker compose -f lab/compose.yaml up -d --build
```

## Supervision infrastructure

La stack principale remonte aussi :

- CPU
- memoire
- disque
- reseau
- metriques conteneurs Docker

Pour relancer avec cette supervision :

```bash
cd /root/Signoz
docker compose up -d
```

## Supervision GPU optionnelle

Si la machine a un GPU NVIDIA :

```bash
cd /root/Signoz
docker compose -f compose.yaml -f compose.gpu.yaml up -d
```

## Volumes Docker

- `signoz-clickhouse`
- `signoz-sqlite`
- `signoz-zookeeper-1`
