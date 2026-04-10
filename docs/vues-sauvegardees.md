# Vues sauvegardées

Les vues sauvegardées dans SigNoz permettent de conserver des filtres et requêtes fréquemment utilisés dans les explorateurs de logs et de traces. Elles évitent de refiltrer manuellement à chaque session.

## Comment créer une vue sauvegardée

### Dans l'explorateur de logs

1. Ouvre `http://localhost:8080`
2. Va dans `Logs` → `Logs Explorer`
3. Applique tes filtres (voir ci-dessous)
4. Clique sur `Save this view` (icône de sauvegarde en haut à droite)
5. Donne un nom à la vue
6. La vue apparaît ensuite dans la liste déroulante `Saved Views`

### Dans l'explorateur de traces

1. Va dans `Traces` → `Traces Explorer`
2. Applique tes filtres
3. Clique sur `Save this view`
4. Donne un nom à la vue

---

## Vues de logs recommandées

### Vue 1 — Erreurs toutes machines

Nom : `Erreurs - toutes machines`

Filtres à appliquer :

- `severity_text` = `ERROR`

Utilité : voir d'un coup toutes les erreurs émises par les 3 machines.

---

### Vue 2 — Logs edge-gateway

Nom : `Logs - edge-gateway`

Filtres à appliquer :

- `service.name` = `edge-gateway`

---

### Vue 3 — Logs orders-api

Nom : `Logs - orders-api`

Filtres à appliquer :

- `service.name` = `orders-api`

---

### Vue 4 — Logs billing-worker

Nom : `Logs - billing-worker`

Filtres à appliquer :

- `service.name` = `billing-worker`

Utilité : c'est ce service qui génère des erreurs volontairement, c'est donc ici que tu verras le plus d'activité intéressante.

---

### Vue 5 — Requêtes échouées

Nom : `Requêtes échouées`

Filtres à appliquer :

- `body` CONTAINS `failed`

Utilité : vue rapide sur tous les messages d'échec de traitement ou d'écriture.

---

### Vue 6 — Logs par environnement

Nom : `Logs - test`

Filtres à appliquer :

- `deployment.environment` = `test`

Utilité : isoler tous les signaux venant de l'environnement de test si tu branches plusieurs environnements.

---

## Vues de traces recommandées

### Vue 1 — Traces en erreur

Nom : `Traces en erreur`

Filtres à appliquer :

- `status` = `error`

Utilité : voir uniquement les traces qui contiennent au moins un span en erreur.

---

### Vue 2 — Traces billing-worker

Nom : `Traces - billing-worker`

Filtres à appliquer :

- `service.name` = `billing-worker`

Utilité : suivre spécifiquement les appels vers le dernier maillon de la chaîne, là où les erreurs se produisent.

---

### Vue 3 — Traces lentes

Nom : `Traces lentes (> 500 ms)`

Filtres à appliquer :

- `duration` > `500` ms

Utilité : isoler les requêtes anormalement lentes pour investigation.

---

### Vue 4 — Flux edge-gateway complet

Nom : `Flux complet - edge-gateway`

Filtres à appliquer :

- `service.name` = `edge-gateway`
- `name` = `GET /api/process`

Utilité : suivre uniquement les appels entrants sur le point d'entrée principal de la chaîne.

---

## Récapitulatif des vues à créer

| Type   | Nom                          | Filtre principal                              |
|--------|------------------------------|-----------------------------------------------|
| Logs   | Erreurs - toutes machines    | severity = ERROR                              |
| Logs   | Logs - edge-gateway          | service.name = edge-gateway                   |
| Logs   | Logs - orders-api            | service.name = orders-api                     |
| Logs   | Logs - billing-worker        | service.name = billing-worker                 |
| Logs   | Requêtes échouées            | body CONTAINS failed                          |
| Logs   | Logs - test                  | deployment.environment = test                 |
| Traces | Traces en erreur             | status = error                                |
| Traces | Traces - billing-worker      | service.name = billing-worker                 |
| Traces | Traces lentes (> 500 ms)     | duration > 500 ms                             |
| Traces | Flux complet - edge-gateway  | service.name = edge-gateway + /api/process    |
