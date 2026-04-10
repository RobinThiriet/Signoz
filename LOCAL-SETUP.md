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

## Verification rapide

```bash
cd /root/Signoz
docker compose ps
curl http://localhost:8080/api/v1/health
```

## Lab de test 3 machines

La stack de test avec trois machines simulees est documentee ici :

- `/root/Signoz/docs/signoz-lab.md`

Demarrage :

```bash
cd /root/Signoz
docker compose -f lab/compose.yaml up -d --build
```

## Volumes Docker

- `signoz-clickhouse`
- `signoz-sqlite`
- `signoz-zookeeper-1`
