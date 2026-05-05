# 🐳 Production Docker Setup

Cette configuration est **uniquement pour la production**. Pour le développement, utilise Celery + Redis en local (voir README racine).

## Déployer

```bash
cd docker-prod

# Build
docker compose build

# Démarrer
docker compose up -d

# Migrations
docker compose exec django python manage.py migrate

# Logs
docker compose logs -f
```

## Services

- **Django** (port 8000) : Web server
- **Celery Worker** : Traitement async
- **Redis** (port 6379) : Broker de messages

## Logs

```bash
docker compose logs django          # Django uniquement
docker compose logs celery-worker   # Celery uniquement
docker compose logs redis           # Redis uniquement
docker compose logs -f              # Tous, en temps réel
```

## Arrêter

```bash
docker compose down          # Arrête sans supprimer les volumes
docker compose down -v       # Arrête ET supprime les volumes
```

---

**Pour développer localement, voir le [README racine](../README.md).**
