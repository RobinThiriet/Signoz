# SigNoz - Version demo en francais

Ce depot contient une version **allegee et prete a presenter** de SigNoz.

Il a ete prepare pour :

- lancer rapidement SigNoz avec Docker Compose
- generer des **traces**, des **logs** et des **metriques**
- montrer un **lab de test avec 3 machines**
- servir de support simple pour une **demo**, un **test** ou une **presentation**

## Contenu du depot

- [compose.yaml](compose.yaml) : stack principale SigNoz
- [LOCAL-SETUP.md](LOCAL-SETUP.md) : guide rapide local
- [lab/compose.yaml](lab/compose.yaml) : lab de demonstration
- [lab/app/machine.py](lab/app/machine.py) : application simulant les 3 machines
- [docs/signoz-lab.md](docs/signoz-lab.md) : documentation detaillee du lab
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

## Premiere connexion et identifiants

Actuellement, l'instance n'a **pas encore de compte configure**.

Verification actuelle :

```json
{"setupCompleted":false}
```

Cela signifie qu'il n'y a **pas d'identifiants par defaut**.

Pour te connecter :

1. ouvre `http://localhost:8080`
2. complete l'ecran d'initialisation
3. cree ton compte administrateur
4. conserve l'email et le mot de passe choisis : ce seront tes identifiants de connexion

En resume :

- identifiant : **l'email que tu vas creer au premier lancement**
- mot de passe : **celui que tu vas definir**
- il n'y a **pas** de login/mot de passe preconfigure dans ce projet

## Connecter une nouvelle application ou machine

SigNoz recoit la telemetrie via OpenTelemetry.

Endpoints disponibles :

- OTLP gRPC : `localhost:4317`
- OTLP HTTP : `http://localhost:4318`

### Cas 1 : application lancee directement sur la machine hote

Si ton application tourne directement sur le serveur ou sur ton PC :

- traces/logs/metriques vers `localhost:4317` en gRPC
- ou vers `http://localhost:4318` en HTTP

Variables d'environnement typiques :

```bash
export OTEL_SERVICE_NAME=mon-application
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_RESOURCE_ATTRIBUTES=service.name=mon-application,deployment.environment=demo
```

### Cas 2 : application dans Docker Compose, sur le meme reseau que SigNoz

Si ton application tourne dans Docker et partage le reseau `signoz-net`, elle doit viser le nom du service :

- `http://signoz-otel-collector:4318`
- ou `signoz-otel-collector:4317`

Exemple :

```yaml
environment:
  OTEL_SERVICE_NAME: mon-service
  OTEL_EXPORTER_OTLP_ENDPOINT: http://signoz-otel-collector:4318
  OTEL_EXPORTER_OTLP_PROTOCOL: http/protobuf
  OTEL_RESOURCE_ATTRIBUTES: service.name=mon-service,deployment.environment=demo
networks:
  - signoz-net
```

### Cas 3 : une autre machine distante

Si tu veux raccorder une autre machine physique ou virtuelle :

- remplace `localhost` par l'IP ou le DNS du serveur qui heberge SigNoz
- ouvre les ports `4317` et/ou `4318` si un pare-feu est actif

Exemple :

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://IP_DU_SERVEUR_SIGNOZ:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
```

## Ce qu'il faut instrumenter

Pour voir les donnees dans SigNoz, ton application doit envoyer au moins un de ces signaux :

- **traces** : appels, latences, erreurs, parcours distribue
- **logs** : journaux applicatifs centralises
- **metriques** : compteurs, erreurs, temps de reponse, jauges

En pratique, tu as 2 options :

1. utiliser les SDK OpenTelemetry de ton langage
2. utiliser un collecteur OpenTelemetry intermediaire si ton architecture est plus complexe

## Exemple minimal d'une nouvelle application Docker

```yaml
services:
  mon-api:
    image: mon-image
    environment:
      OTEL_SERVICE_NAME: mon-api
      OTEL_EXPORTER_OTLP_ENDPOINT: http://signoz-otel-collector:4318
      OTEL_EXPORTER_OTLP_PROTOCOL: http/protobuf
      OTEL_RESOURCE_ATTRIBUTES: service.name=mon-api,deployment.environment=demo
    networks:
      - signoz-net

networks:
  signoz-net:
    external: true
```

Une fois l'application demarree, elle apparaitra dans SigNoz dans les vues :

- `Services`
- `Traces`
- `Logs`
- `Metrics`

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

- guide local rapide : [LOCAL-SETUP.md](LOCAL-SETUP.md)
- documentation du lab et schema reseau : [docs/signoz-lab.md](docs/signoz-lab.md)
- schema d'architecture : [docs/schema-architecture.md](docs/schema-architecture.md)
- dashboards et alertes : [docs/dashboards-alertes.md](docs/dashboards-alertes.md)
- vues sauvegardees : [docs/vues-sauvegardees.md](docs/vues-sauvegardees.md)
- guide creation manuelle (dashboards, alertes, vues) : [docs/guide-ui.md](docs/guide-ui.md)

## Objectif de cette version

Cette version n'est pas le depot complet de developpement de SigNoz.

C'est une version **simple**, **legere** et **orientee demonstration** afin de :

- presenter SigNoz facilement
- lancer un environnement de test rapidement
- montrer les fonctions principales sans garder tout le code source d'origine
