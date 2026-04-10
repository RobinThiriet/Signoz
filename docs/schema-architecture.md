# Schéma d'architecture

Ce schéma présente l'architecture de la démonstration SigNoz avec la plateforme d'observabilité et les 3 machines simulées.

## Vue d'ensemble

```mermaid
flowchart LR
    U[Utilisateur / Navigateur]

    subgraph Plateforme["Plateforme SigNoz"]
        UI[Interface SigNoz<br/>localhost:8080]
        COL[Collecteur OpenTelemetry<br/>localhost:4317 / 4318]
        CH[(ClickHouse)]
        ZK[(ZooKeeper)]
        DB[(SQLite SigNoz)]
    end

    subgraph Lab["Lab de test"]
        M1[Machine 1<br/>edge-gateway<br/>localhost:18081]
        M2[Machine 2<br/>orders-api<br/>localhost:18082]
        M3[Machine 3<br/>billing-worker<br/>localhost:18083]
    end

    U --> UI

    M1 -->|HTTP /api/process| M2
    M2 -->|HTTP /api/store| M3

    M1 -. Traces / Logs / Metriques .-> COL
    M2 -. Traces / Logs / Metriques .-> COL
    M3 -. Traces / Logs / Metriques .-> COL

    COL --> CH
    UI --> CH
    UI --> DB
    CH --> ZK
```

## Lecture simple du schéma

- L'utilisateur accède à SigNoz via l'interface web.
- Les trois machines du lab simulent une petite application distribuée.
- Chaque machine envoie ses traces, logs et métriques au collecteur OpenTelemetry de SigNoz.
- Le collecteur stocke les données d'observabilité dans ClickHouse.
- SigNoz lit ces données pour les afficher dans les vues traces, logs, métriques et alertes.

## Flux applicatif

```mermaid
sequenceDiagram
    participant Client as Générateur de trafic
    participant M1 as Machine 1 - edge-gateway
    participant M2 as Machine 2 - orders-api
    participant M3 as Machine 3 - billing-worker
    participant COL as Collecteur OTLP
    participant UI as Interface SigNoz

    Client->>M1: requête synthétique
    M1->>M2: /api/process
    M2->>M3: /api/store

    M1-->>COL: traces + logs + métriques
    M2-->>COL: traces + logs + métriques
    M3-->>COL: traces + logs + métriques

    COL-->>UI: données exploitables
```

## Points à expliquer à l'oral

- SigNoz centralise les 3 piliers de l'observabilité : traces, logs et métriques.
- Le lab crée un parcours distribué entre 3 services.
- `billing-worker` produit volontairement des erreurs pour rendre la démonstration visible.
- Les alertes peuvent être construites à partir des métriques `lab_*` ou des erreurs visibles dans les traces et les logs.
