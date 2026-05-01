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

---

# WhatsApp Sentiment Analysis Bot

A Django bot to analyze sentiments of WhatsApp messages via Meta's Cloud API.

## Features

- Receive WhatsApp messages via webhook
- Store messages in a database
- Sentiment analysis (to be implemented)
- Django admin interface to view messages

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Deleya/whatsapp-sentiment.git
   cd whatsapp-sentiment
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root:
   ```env
   DEBUG=True
   SECRET_KEY=your_secret_key
   WHATSAPP_VERIFY_TOKEN=your_verification_token
   ALLOWED_HOSTS=localhost,127.0.0.1,.ngrok-free.app
   ```

5. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (optional, for admin):
   ```bash
   python manage.py createsuperuser
   ```

## Usage

### Run the development server
```bash
python manage.py runserver
```

The server will be accessible at `http://127.0.0.1:8000/`.

### Configure WhatsApp webhook

1. **Use ngrok** to expose the local server:
   ```bash
   ngrok http 8000
   ```
   This gives a URL like `https://abcd1234.ngrok-free.app`.

2. **Configure in Meta for Developers**:
   - Callback URL: `https://abcd1234.ngrok-free.app/webhook/`
   - Verify Token: the one defined in `.env`

3. **Test**:
   - Send a message on connected WhatsApp.
   - Check in Django admin: `http://127.0.0.1:8000/admin/`

## Project Structure

```
whatsapp_sentiment/
├── apps/
│   ├── core/          # Main app
│   └── whatsapp_bot/  # WhatsApp bot logic
├── config/            # Django configuration
├── db.sqlite3         # Database
├── manage.py          # Django management script
└── .env               # Environment variables
```

## Technologies Used

- **Django**: Web framework
- **WhatsApp Cloud API**: To receive messages
- **SQLite**: Database (easily replaceable with PostgreSQL)
- **python-decouple**: Environment variable management

## Development

### Add sentiment analysis

In `apps/whatsapp_bot/models.py`, the `sentiment_score` and `sentiment_label` fields are ready.

Implement the logic in `views.py` or create a Celery task to analyze received messages.

### Deployment

For production:
- Use a WSGI server like Gunicorn
- Configure a reverse proxy (Nginx)
- Use a robust database (PostgreSQL)
- Secure with HTTPS

## License

MIT