# Helpdesk — internal IT support ticketing

**English** · [Français](#helpdesk--gestion-de-tickets-du-support-informatique-interne)

Ticketing web application for the IT support team of a logistics SME (~200 employees,
several sites). It replaces a workflow built on e-mail and a shared spreadsheet: every
incident becomes a traceable ticket with a priority, a resolution deadline, an assigned
technician, a status history and attachments.

**Stack**: Python 3.10+ · Flask 3.1 · SQLAlchemy 2.0 · Alembic (Flask-Migrate) ·
PostgreSQL 18 · WTForms · PyJWT · argon2 · Jinja2 + Tailwind · Docker Compose

---

## Contents

- [Features](#features)
- [Quick start](#quick-start)
- [Architecture](#architecture)
- [The in-house framework](#the-in-house-framework)
- [Data model](#data-model)
- [Security](#security)
- [Technical choices and trade-offs](#technical-choices-and-trade-offs)
- [Known limitations and roadmap](#known-limitations-and-roadmap)

---

## Features

Three roles, which can be combined (many-to-many `users` ↔ `roles`):

| Role | Scope |
|---|---|
| `CLIENT` | Opens tickets, follows their own, comments, attaches files |
| `TECHNICIEN` | Sees every ticket, moves them through their lifecycle |
| `ADMIN` | Full access: users, teams, categories, priorities |

- **Ticket lifecycle** — `NEW → IN_PROGRESS → BLOCKED → RESOLVED → CLOSED`, typed by a
  PostgreSQL `ENUM`. Every transition writes a row to an **immutable history**
  (author, previous status, new status, timestamp).
- **Priority-based SLA** — the deadline is computed at creation from the priority's
  delay (`Urgent` 2 h, `High` 8 h, `Medium` 24 h, `Low` 48 h).
- **Attachments** — controlled upload (extension and MIME type allowlists, 10 MB max),
  stored outside the web root, protected download.
- **Comments** per ticket, editable only by their author.
- **Reference data** — categories, priorities, teams, sites, hardware inventory.
- **Dashboards** for clients and for the support team.

---

## Quick start

Requirements: Docker and Docker Compose.

```bash
# 1. Start the app, PostgreSQL and Mailpit
docker compose up -d

# 2. Apply the migrations
docker compose exec app ./sqlAlchemy.sh -u

# 3. Load the demo dataset (DEBUG mode only)
open http://localhost:8080/seed
```

| Service | URL / port |
|---|---|
| Application | http://localhost:8080 |
| PostgreSQL (external SQL client) | `localhost:5435` |
| Mailpit (dev inbox) | http://localhost:8025 |

Configuration lives in `.env` (versioned, no secrets). Any variable already set in the
environment takes precedence over `.env`. The demo accounts (one admin, one client,
three technicians) are defined in [app/seed/\_\_init\_\_.py](app/seed/__init__.py);
their shared password is read from the `SEED_PASSWORD` variable.

### Migrations

```bash
./sqlAlchemy.sh -m "message"   # generate a migration from the models
./sqlAlchemy.sh -u             # apply
```

---

## Architecture

Strict layered architecture: each layer only knows the one below it, and the database
is reachable from the services only.

```
  Browser
      │  HTTP request (form + CSRF token, JWT cookie)
      ▼
  Controller ─── @auth_required ── @inject
      │  validates the Form, delegates, picks the view
      ▼
  Service ──────── the only layer touching db.session
      │  business rules, transactions, rollback
      ▼
  Mapper ───────── Form → Entity → DTO
      │
      ▼
  Entity (SQLAlchemy) ── PostgreSQL

  The service returns a DTO; templates never see an entity.
```

```
app/
├── framework/      Reusable technical core (DI, seeding, abstract contracts)
├── models/         SQLAlchemy entities
├── forms/          WTForms forms and shared validators
├── dtos/           Transfer objects exposed to views
├── mappers/        Conversions between layers
├── services/       Business logic and data access
├── controllers/    HTTP routes
├── seed/           Demo datasets
├── templates/      Jinja2: layout, reusable macros, pages
└── static/
migrations/         Alembic history
```

**Why DTOs instead of entities in templates?** An entity stays bound to the SQLAlchemy
session: a lazy load inside a template fires an unexpected query, or raises a
`DetachedInstanceError` once the session is closed. A DTO is a frozen snapshot with no
sensitive fields (the password hash never leaves the service), and it decouples views
from the schema: renaming a column only touches the mapper.

---

## The in-house framework

[app/framework/](app/framework/) holds a deliberately minimal core, with no external
dependency, that removes all manual wiring.

### Dependency injection

An in-house container ([injector.py](app/framework/injector.py)) handles three
lifetimes:

| Scope | Lifetime | Use |
|---|---|---|
| `SINGLETON` | the process | stateless services (default) |
| `SCOPED` | one HTTP request (stored in `flask.g`) | services tied to the current user |
| `TRANSIENT` | one call | throwaway instances |

Services register themselves; controllers state their needs through type annotations:

```python
@injectable(base=AbstractAuthService, scope=Scope.SCOPED)
class AuthService(AbstractAuthService): ...

@app.route("/tickets/user")
@auth_required()
@inject
def display_user_tickets(auth_service: AbstractAuthService,
                         ticket_service: TicketService): ...
```

The controller depends on the abstraction; the injector supplies the implementation.
A `config` hook swaps in a test double without touching the calling code:

```python
Injector(app, config=lambda c: c.bind(
    DependencyConfig(UserService, FakeUserService, Scope.SINGLETON)))
```

`@inject` never overrides an argument Flask already provides (URL parameters such as
`<int:ticket_id>`), and a `SCOPED` service requested outside a request (CLI, shell)
cleanly falls back to a transient instance.

### Auto-discovery

Models, controllers, services and seeders register without any list to maintain. Each
package builds its `__all__` from its own contents, and classes register themselves
when they are declared — through a decorator (`@injectable`) or `__init_subclass__`
(`Seedable`). **Adding a service, a route or a dataset means creating a file.**

### Seeding

Each seeder extends `Seedable` and declares an `order` encoding the dependencies
between datasets (roles → users → sites → hardware → tickets → history → surveys). A
failing seeder is isolated by a `rollback`: without it, the aborted transaction would
"poison" the session and make every following seeder fail in cascade, hiding the real
culprit. The `/seed` route is **only registered in debug mode**: in production it
simply does not exist.

### Contracts

`AbstractService`, `AbstractMapper`, `AbstractDTO` and `AbstractAuthService` define a
uniform API (`find_all`, `find_one`, `find_one_entity`, `insert`, `update`,
`delete`…). Convention: a service returns DTOs; `*_entity` methods are reserved for
service-to-service calls.

---

## Data model

15 tables, all carrying the technical columns inherited from the `BaseEntity` mixin
(`created_at`, `updated_at`, `deleted_at`, `active`).

```
                 roles ──N:N── users ──N:1── teams
                                 │  └──N:1── sites ──1:N── equipments
                                 │                              │
       categories ──1:N──┐       │ author / technician          │
       priorities ──1:N──┤       ▼                              │
                         └──── tickets ◄────────────────────────┘
                                 │
         ┌──────────────┬────────┼──────────────┬───────────────────┐
     comments     attachments   ticketstatushistories   satisfactionsurveys (1:1)

       knowledgearticles ──N:1── categories, users
```

Modelling notes:

- **Two `tickets` → `users` relationships** (author and assigned technician),
  disambiguated with explicit `foreign_keys` on both sides.
- **Soft delete**: a deactivated user keeps their tickets, comments and history; the
  referential integrity of the history is never broken.
- **Status typed in the database**: migration
  [794318362016](migrations/versions/794318362016_ticket_status_as_enum.py) converts
  three `VARCHAR` columns to a shared PostgreSQL `ENUM`, casting with
  `USING status::ticketstatusenum` to preserve existing data. The type is created once,
  explicitly: left implicit, Alembic would try to recreate it for each column and fail
  on the second one.
- **Append-only history**: `TicketStatusHistoryService.delete()` deliberately raises.

---

## Security

| Topic | Implementation |
|---|---|
| Passwords | argon2id (`argon2-cffi`), **transparent rehash** on login when cost parameters change |
| Account enumeration | a login attempt on an unknown user still computes a hash: identical response time |
| Session | HS256 JWT in an `HttpOnly`, `SameSite=Lax` cookie, configurable expiry |
| CSRF | global `CSRFProtect`: also covers POST actions without a WTForms form (deletions) |
| Authorization | `@auth_required(role_name=…, is_current_user=…)`: required role, or resource owner; admins always pass |
| Uploads | double allowlist (extension + MIME), size checked before **and** after writing, UUID storage name, file cleaned up if the transaction fails |
| Path traversal | path resolved with `realpath` and confined to the upload folder before any download |
| Password policy | 12 to 80 characters, lowercase, uppercase, digit and special character in production; relaxed in debug for development comfort |
| Debug surface | Debug Toolbar and `/seed` gated behind `DEBUG` |

The JWT travels through `flask.g` to an `after_request` hook that sets or clears the
cookie: authentication services stay unaware of the `Response` object.

---

## Technical choices and trade-offs

**An in-house DI container rather than a library.** The need fits in about a hundred
lines: resolution by type name, three scopes, test substitution. An external
dependency would have added an API to learn for no gain, and the mechanism stays
readable by the whole team.

**No Blueprints.** Controller auto-discovery covers the modularity need; Blueprints
become relevant once a versioned API (`/api/v1`) has to live alongside the web UI.

**JWT rather than server-side sessions.** The token is stateless and can be reused
as-is by a future API consumed outside the browser. The trade-off: revoking before
expiry requires a denylist; the short lifetime (1 h by default) limits the stakes.

**Mailpit in development.** The dev SMTP server captures every message and delivers
none: transactional e-mails can be worked on without any risk of reaching real
recipients.

---

## Known limitations and roadmap

The project is under active development. The following is identified and prioritised:

- **Automated tests** — the injector's substitution hook is in place; the `pytest`
  suite comes next (services first, then HTTP tests through the Flask client).
- **Status transitions** — the "a client does not change the status" rule and the
  graph of allowed transitions must move into a `Ticket.change_status()` domain
  method, so the rule lives with the entity rather than in the controller.
- **Deadline precision** — `due_date` is a `DATE` column while the SLA is counted in
  hours: an `Urgent` ticket loses its cut-off time. Migration to
  `TIMESTAMP WITH TIME ZONE` planned.
- **JSON API** — `/api/users` awaits `Authorization: Bearer` header authentication
  before being exposed.
- **E-mail notifications** — SMTP infrastructure ready (Mailpit); sending (password
  reset, status change) still to be wired.
- **Production deployment** — WSGI server (gunicorn), `Secure` cookie behind HTTPS,
  secrets injected exclusively through the environment.
- **Knowledge base and satisfaction surveys** — models and data in place, interfaces
  to be built.

<br>

---
---

# Helpdesk — gestion de tickets du support informatique interne

[English](#helpdesk--internal-it-support-ticketing) · **Français**

Application web de ticketing pour le support informatique d'une PME de logistique
(~200 collaborateurs, plusieurs sites). Elle remplace un traitement des demandes par
e-mail et tableur partagé : chaque incident devient un ticket traçable, avec une
priorité, un délai de résolution, un technicien, un historique de statuts et des
pièces jointes.

**Stack** : Python 3.10+ · Flask 3.1 · SQLAlchemy 2.0 · Alembic (Flask-Migrate) ·
PostgreSQL 18 · WTForms · PyJWT · argon2 · Jinja2 + Tailwind · Docker Compose

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Démarrage rapide](#démarrage-rapide)
- [Architecture](#architecture-1)
- [Le framework interne](#le-framework-interne)
- [Modèle de données](#modèle-de-données)
- [Sécurité](#sécurité)
- [Choix techniques et compromis](#choix-techniques-et-compromis)
- [Limites connues et suite](#limites-connues-et-suite)

---

## Fonctionnalités

Trois rôles, cumulables (relation N-N `users` ↔ `roles`) :

| Rôle | Périmètre |
|---|---|
| `CLIENT` | Ouvre des tickets, suit les siens, commente, joint des fichiers |
| `TECHNICIEN` | Voit l'ensemble des tickets, fait évoluer leur statut |
| `ADMIN` | Accès complet : utilisateurs, équipes, catégories, priorités |

- **Cycle de vie des tickets** — `NEW → IN_PROGRESS → BLOCKED → RESOLVED → CLOSED`,
  typé par un `ENUM` PostgreSQL. Chaque transition écrit une ligne dans un
  **historique immuable** (auteur, ancien statut, nouveau statut, horodatage).
- **SLA par priorité** — l'échéance est calculée à la création à partir du délai de
  la priorité (`Urgent` 2 h, `High` 8 h, `Medium` 24 h, `Low` 48 h).
- **Pièces jointes** — upload contrôlé (liste blanche d'extensions et de types MIME,
  10 Mo max), stockage hors de la racine web, téléchargement protégé.
- **Commentaires** par ticket, éditables uniquement par leur auteur.
- **Référentiels** — catégories, priorités, équipes, sites, parc matériel.
- **Tableaux de bord** distincts côté client et côté support.

---

## Démarrage rapide

Prérequis : Docker et Docker Compose.

```bash
# 1. Lancer l'application, PostgreSQL et Mailpit
docker compose up -d

# 2. Appliquer les migrations
docker compose exec app ./sqlAlchemy.sh -u

# 3. Charger le jeu de données de démonstration (mode DEBUG uniquement)
open http://localhost:8080/seed
```

| Service | URL / port |
|---|---|
| Application | http://localhost:8080 |
| PostgreSQL (client SQL externe) | `localhost:5435` |
| Mailpit (boîte de réception de dev) | http://localhost:8025 |

La configuration vit dans `.env` (versionné, sans secret). Toute variable déjà
définie dans l'environnement prime sur `.env`. Les comptes de démonstration (un admin, un
client, trois techniciens) sont définis dans [app/seed/\_\_init\_\_.py](app/seed/__init__.py) ;
leur mot de passe commun est lu dans la variable `SEED_PASSWORD`.

### Migrations

```bash
./sqlAlchemy.sh -m "message"   # générer une migration depuis les modèles
./sqlAlchemy.sh -u             # appliquer
```

---

## Architecture

Architecture en couches stricte : chaque couche ne connaît que celle du dessous, et
la base de données n'est accessible que depuis les services.

```
  Navigateur
      │  requête HTTP (formulaire + jeton CSRF, cookie JWT)
      ▼
  Controller ─── @auth_required ── @inject
      │  valide le Form, délègue, choisit la vue
      ▼
  Service ──────── seule couche qui touche db.session
      │  règles métier, transactions, rollback
      ▼
  Mapper ───────── Form → Entity → DTO
      │
      ▼
  Entity (SQLAlchemy) ── PostgreSQL

  Le service renvoie un DTO ; le template ne voit jamais une entité.
```

```
app/
├── framework/      Socle technique réutilisable (DI, seeding, contrats abstraits)
├── models/         Entités SQLAlchemy
├── forms/          Formulaires WTForms et validateurs partagés
├── dtos/           Objets de transfert exposés aux vues
├── mappers/        Conversions entre couches
├── services/       Logique métier et accès aux données
├── controllers/    Routes HTTP
├── seed/           Jeux de données de démonstration
├── templates/      Jinja2 : layout, macros réutilisables, pages
└── static/
migrations/         Historique Alembic
```

**Pourquoi des DTO plutôt que les entités dans les templates ?** Une entité reste
attachée à la session SQLAlchemy : un accès paresseux dans un template déclenche une
requête imprévue, ou une `DetachedInstanceError` si la session est close. Le DTO est
un instantané figé, sans champ sensible (le hash du mot de passe ne sort jamais du
service), et il découple les vues du schéma : renommer une colonne ne touche que le
mapper.

---

## Le framework interne

Le dossier [app/framework/](app/framework/) contient un socle volontairement
minimal, sans dépendance externe, qui supprime tout câblage manuel.

### Injection de dépendances

Un conteneur maison ([injector.py](app/framework/injector.py)) gère trois durées de
vie :

| Scope | Durée de vie | Usage |
|---|---|---|
| `SINGLETON` | le processus | services sans état (défaut) |
| `SCOPED` | une requête HTTP (stocké dans `flask.g`) | services liés à l'utilisateur courant |
| `TRANSIENT` | un appel | instances jetables |

Les services se déclarent eux-mêmes ; les controllers expriment leurs besoins par
annotation de type :

```python
@injectable(base=AbstractAuthService, scope=Scope.SCOPED)
class AuthService(AbstractAuthService): ...

@app.route("/tickets/user")
@auth_required()
@inject
def display_user_tickets(auth_service: AbstractAuthService,
                         ticket_service: TicketService): ...
```

Le controller dépend de l'abstraction, l'injecteur livre l'implémentation. Un
crochet `config` permet de substituer un double de test sans modifier le code
appelant :

```python
Injector(app, config=lambda c: c.bind(
    DependencyConfig(UserService, FakeUserService, Scope.SINGLETON)))
```

`@inject` ne remplace jamais un argument déjà fourni par Flask (paramètres d'URL
comme `<int:ticket_id>`), et un service `SCOPED` appelé hors requête (CLI, shell)
retombe proprement sur une instance transitoire.

### Auto-découverte

Modèles, controllers, services et seeders s'enregistrent sans liste à maintenir.
Chaque package construit son `__all__` à partir de son contenu, et les classes
s'inscrivent au moment de leur déclaration — par décorateur (`@injectable`) ou par
`__init_subclass__` (`Seedable`). **Ajouter un service, une route ou un jeu de
données revient à créer un fichier.**

### Seeding

Chaque seeder hérite de `Seedable` et déclare un `order` qui encode les dépendances
entre données (rôles → utilisateurs → sites → matériel → tickets → historiques →
enquêtes). Un seeder en échec est isolé par un `rollback` : sans lui, la transaction
avortée « empoisonnerait » la session et ferait échouer en cascade tous les seeders
suivants, masquant le vrai coupable. La route `/seed` n'est **enregistrée qu'en mode
debug** : elle n'existe tout simplement pas en production.

### Contrats

`AbstractService`, `AbstractMapper`, `AbstractDTO` et `AbstractAuthService` fixent
une API uniforme (`find_all`, `find_one`, `find_one_entity`, `insert`, `update`,
`delete`…). Convention : un service renvoie des DTO ; les méthodes `*_entity` sont
réservées aux échanges entre services.

---

## Modèle de données

15 tables, toutes dotées des colonnes techniques héritées du mixin `BaseEntity`
(`created_at`, `updated_at`, `deleted_at`, `active`).

```
                 roles ──N:N── users ──N:1── teams
                                 │  └──N:1── sites ──1:N── equipments
                                 │                              │
       categories ──1:N──┐       │ auteur / technicien          │
       priorities ──1:N──┤       ▼                              │
                         └──── tickets ◄────────────────────────┘
                                 │
         ┌──────────────┬────────┼──────────────┬───────────────────┐
     comments     attachments   ticketstatushistories   satisfactionsurveys (1:1)

       knowledgearticles ──N:1── categories, users
```

Points de modélisation :

- **Double relation `tickets` → `users`** (auteur et technicien assigné), levée par
  `foreign_keys` explicites de part et d'autre.
- **Soft delete** : un utilisateur désactivé conserve ses tickets, commentaires et
  historiques ; l'intégrité référentielle de l'historique n'est jamais rompue.
- **Statut typé en base** : la migration
  [794318362016](migrations/versions/794318362016_ticket_status_as_enum.py) convertit
  trois colonnes `VARCHAR` vers un `ENUM` PostgreSQL partagé, avec cast
  `USING status::ticketstatusenum` pour préserver les données existantes. Le type est
  créé une seule fois, explicitement : laissé implicite, Alembic tenterait de le
  recréer à chaque colonne et échouerait dès la deuxième.
- **Historique en ajout seul** : `TicketStatusHistoryService.delete()` lève
  volontairement une exception.

---

## Sécurité

| Sujet | Mise en œuvre |
|---|---|
| Mots de passe | argon2id (`argon2-cffi`), **rehash transparent** au login si les paramètres de coût évoluent |
| Énumération de comptes | un login sur un utilisateur inconnu calcule quand même un hash : temps de réponse identique |
| Session | JWT HS256 dans un cookie `HttpOnly`, `SameSite=Lax`, expiration configurable |
| CSRF | `CSRFProtect` global : couvre aussi les actions POST sans formulaire WTForms (suppressions) |
| Autorisation | `@auth_required(role_name=…, is_current_user=…)` : rôle requis, ou propriétaire de la ressource ; l'admin passe toujours |
| Uploads | double liste blanche extension + MIME, taille vérifiée avant **et** après écriture, nom de stockage UUID, nettoyage du fichier si la transaction échoue |
| Path traversal | chemin résolu par `realpath` et confiné au dossier d'upload avant tout téléchargement |
| Politique de mots de passe | 12 à 80 caractères, minuscule, majuscule, chiffre et caractère spécial en production ; assouplie en debug pour le confort de développement |
| Surface de debug | Debug Toolbar et `/seed` conditionnés à `DEBUG` |

Le JWT transite par `flask.g` jusqu'à un hook `after_request` qui pose ou supprime le
cookie : les services d'authentification restent ignorants de l'objet `Response`.

---

## Choix techniques et compromis

**Un conteneur DI maison plutôt qu'une bibliothèque.** Le besoin tient en une
centaine de lignes : résolution par nom de type, trois scopes, substitution en test.
Une dépendance externe aurait ajouté une API à apprendre pour un gain nul, et le
mécanisme reste lisible par toute l'équipe.

**Pas de Blueprints.** L'auto-découverte des controllers couvre le besoin de
modularité ; les Blueprints deviendront pertinents si une API versionnée (`/api/v1`)
doit coexister avec l'interface web.

**JWT plutôt que session serveur.** Le jeton est sans état et réutilisable tel quel
par une future API consommée hors navigateur. En contrepartie, la révocation avant
expiration demande une liste noire ; la durée de vie courte (1 h par défaut) en
limite l'enjeu.

**Mailpit en développement.** Le serveur SMTP de dev capture tous les envois sans en
livrer aucun : on travaille les e-mails transactionnels sans risque d'écrire à de
vrais destinataires.

---

## Limites connues et suite

Le projet est en développement actif. Ce qui suit est identifié et priorisé :

- **Tests automatisés** — le crochet de substitution de l'injecteur est en place ;
  reste à poser la suite `pytest` (services d'abord, puis tests HTTP via le client
  Flask).
- **Transitions de statut** — la règle « un client ne modifie pas le statut » et le
  graphe des transitions autorisées doivent descendre dans une méthode métier
  `Ticket.change_status()`, pour que la règle vive avec l'entité et non dans le
  controller.
- **Précision de l'échéance** — `due_date` est une colonne `DATE` alors que le SLA se
  compte en heures : un ticket `Urgent` perd son heure limite. Migration prévue vers
  `TIMESTAMP WITH TIME ZONE`.
- **API JSON** — `/api/users` attend une authentification par en-tête
  `Authorization: Bearer` avant d'être exposée.
- **Notifications e-mail** — infrastructure SMTP prête (Mailpit), envois
  (réinitialisation de mot de passe, changement de statut) à brancher.
- **Mise en production** — serveur WSGI (gunicorn), cookie `Secure` derrière HTTPS,
  secrets exclusivement injectés par l'environnement.
- **Base de connaissances et enquêtes de satisfaction** — modèles et données en
  place, interfaces à construire.
