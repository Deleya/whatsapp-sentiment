# WhatsApp Sentiment Analysis Bot

Un bot Django pour analyser les sentiments des messages WhatsApp via l'API Cloud de Meta.

## Fonctionnalités

- Réception de messages WhatsApp via webhook
- Stockage des messages dans une base de données
- Analyse de sentiment (à implémenter)
- Interface d'administration Django pour visualiser les messages

## Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/Deleya/whatsapp-sentiment.git
   cd whatsapp-sentiment
   ```

2. **Créer un environnement virtuel** :
   ```bash
   python -m venv venv
   # Sur Windows :
   venv\Scripts\activate
   # Sur Linux/Mac :
   source venv/bin/activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement** :
   Créer un fichier `.env` à la racine :
   ```env
   DEBUG=True
   SECRET_KEY=votre_clé_secrète
   WHATSAPP_VERIFY_TOKEN=votre_token_de_vérification
   ALLOWED_HOSTS=localhost,127.0.0.1,.ngrok-free.app
   ```

5. **Appliquer les migrations** :
   ```bash
   python manage.py migrate
   ```

6. **Créer un superutilisateur** (optionnel, pour l'admin) :
   ```bash
   python manage.py createsuperuser
   ```

## Utilisation

### Lancer le serveur de développement
```bash
python manage.py runserver
```

Le serveur sera accessible sur `http://127.0.0.1:8000/`.

### Configuration du webhook WhatsApp

1. **Utiliser ngrok** pour exposer le serveur local :
   ```bash
   ngrok http 8000
   ```
   Cela donne une URL comme `https://abcd1234.ngrok-free.app`.

2. **Configurer dans Meta for Developers** :
   - Callback URL : `https://abcd1234.ngrok-free.app/webhook/`
   - Verify Token : celui défini dans `.env`

3. **Tester** :
   - Envoyer un message sur WhatsApp connecté.
   - Vérifier dans l'admin Django : `http://127.0.0.1:8000/admin/`

## Structure du projet

```
whatsapp_sentiment/
├── apps/
│   ├── core/          # App principale
│   └── whatsapp_bot/  # Logique du bot WhatsApp
├── config/            # Configuration Django
├── db.sqlite3         # Base de données
├── manage.py          # Script de gestion Django
└── .env               # Variables d'environnement
```

## Technologies utilisées

- **Django** : Framework web
- **WhatsApp Cloud API** : Pour recevoir les messages
- **SQLite** : Base de données (facilement remplaçable par PostgreSQL)
- **python-decouple** : Gestion des variables d'environnement

## Développement

### Ajouter l'analyse de sentiment

Dans `apps/whatsapp_bot/models.py`, les champs `sentiment_score` et `sentiment_label` sont prêts.

Implémentez la logique dans `views.py` ou créez une tâche Celery pour analyser les messages reçus.

### Déploiement

Pour la production :
- Utiliser un serveur WSGI comme Gunicorn
- Configurer un reverse proxy (Nginx)
- Utiliser une base de données robuste (PostgreSQL)
- Sécuriser avec HTTPS

## Licence

MIT