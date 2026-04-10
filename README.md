# SigNoz - Version demo en francais

Ce depot contient une version **allegee et prete a presenter** de SigNoz.

Il a ete prepare pour :

- lancer rapidement SigNoz avec Docker Compose
- generer des **traces**, des **logs** et des **metriques**
- montrer un **lab de test avec 3 machines**
- servir de support simple pour une **demo**, un **test** ou une **presentation**

## Contenu du depot

- [compose.yaml](/root/Signoz/compose.yaml) : stack principale SigNoz
- [LOCAL-SETUP.md](/root/Signoz/LOCAL-SETUP.md) : guide rapide local
- [lab/compose.yaml](/root/Signoz/lab/compose.yaml) : lab de demonstration
- [lab/app/machine.py](/root/Signoz/lab/app/machine.py) : application simulant les 3 machines
- [docs/signoz-lab.md](/root/Signoz/docs/signoz-lab.md) : documentation detaillee du lab
- `deploy/common/clickhouse/` : configuration minimale ClickHouse
- `deploy/docker/otel-collector-config.yaml` : configuration du collecteur OTLP

## Prerequis

- Docker
- Docker Compose

## Lancer SigNoz

```bash
cd /root/Signoz
docker compose up -d
```

Acces :

- interface SigNoz : `http://localhost:8080`
- OTLP gRPC : `localhost:4317`
- OTLP HTTP : `http://localhost:4318`

## Verifier que SigNoz fonctionne

```bash
cd /root/Signoz
docker compose ps
curl http://localhost:8080/api/v1/health
```

Reponse attendue :

```json
{"status":"ok"}
```

## Lancer le lab de test

Le lab simule 3 services :

- `edge-gateway`
- `orders-api`
- `billing-worker`

Il genere automatiquement :

- des traces distribuees
- des logs applicatifs
- des metriques custom
- des erreurs volontaires pour tester l'observabilite et les alertes

Demarrage :

```bash
cd /root/Signoz
docker compose -f lab/compose.yaml up -d --build
```

Acces :

- machine 1 : `http://localhost:18081`
- machine 2 : `http://localhost:18082`
- machine 3 : `http://localhost:18083`

## Verifier le lab

```bash
curl http://localhost:18081/health
curl http://localhost:18082/health
curl http://localhost:18083/health
```

Ensuite ouvre SigNoz sur `http://localhost:8080`.

Tu devrais voir remonter rapidement :

- les services `edge-gateway`, `orders-api` et `billing-worker`
- des traces distribuees
- des logs applicatifs
- des metriques commencant par `lab_`

## Arreter les services

Arreter le lab :

```bash
cd /root/Signoz
docker compose -f lab/compose.yaml down
```

Arreter SigNoz :

```bash
cd /root/Signoz
docker compose down
```

## Documentation

- guide local rapide : [LOCAL-SETUP.md](/root/Signoz/LOCAL-SETUP.md)
- documentation du lab et schema reseau : [docs/signoz-lab.md](/root/Signoz/docs/signoz-lab.md)

## Objectif de cette version

Cette version n'est pas le depot complet de developpement de SigNoz.

C'est une version **simple**, **legere** et **orientee demonstration** afin de :

- presenter SigNoz facilement
- lancer un environnement de test rapidement
- montrer les fonctions principales sans garder tout le code source d'origine
