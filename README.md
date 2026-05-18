# 🤖 WhatsApp Sentiment Bot - Asynchrone avec Celery

Bot WhatsApp qui analyse le sentiment des messages et génère des réponses IA en temps réel, sans bloquer le serveur.

## 🎯 Architecture

```
Message WhatsApp → Meta Webhook → Django (0.05s) → 200 OK (immédiat)
                                      ↓
                                 Redis Queue
                                      ↓
                            Celery Worker (2-5s)
                        • Analyse sentiment (IA)
                        • Génère réponse (Groq)
                        • Envoie WhatsApp
```

**Clé** : Django répond **immédiatement** sans attendre le traitement IA.

---

## 🚀 Démarrage Local (3 terminaux)

### 1. Installer Redis (Memurai sur Windows)

Télécharge : https://www.memurai.com/

Valide : `redis-cli ping` → `PONG`

### 2. Terminal 1 : Django

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

### 3. Terminal 2 : Celery Worker

```powershell
.\.venv\Scripts\Activate.ps1
celery -A config worker -l info
```

### 4. Terminal 3 : Redis

```powershell
# Memurai tourne déjà (service Windows)
redis-cli ping  # Valide que Redis répond
```

---

## 📁 Structure clé

```
apps/whatsapp_bot/
├── models.py          # Message (avec déduplication)
├── views.py           # Webhook Django
├── celery_tasks.py    # Tâche async ⭐
├── nlp_utils.py       # Sentiment
├── agent_brain.py     # IA (Groq)
└── whatsapp_sender.py # Envoi WhatsApp

config/
├── celery.py          # Config Celery ⭐
├── settings.py        # Django + Redis
└── urls.py            # Routes
```

---

## ⚙️ Configuration (.env)

```env
# Django
SECRET_KEY=your_secret_key
DEBUG=False

# WhatsApp
WHATSAPP_VERIFY_TOKEN=your_token
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_id

# Groq API
GROQ_API_KEY=your_groq_api_key

# Redis (défault : localhost)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## 🔐 Déduplication (Pas de doubles)

Utilise `whatsapp_message_id` (ID externe Meta) comme clé unique :

```python
# models.py
class Message(models.Model):
    whatsapp_message_id = models.CharField(
        max_length=128,
        unique=True,        # ← Empêche les doubles
        null=True,
        blank=True,
        db_index=True       # ← Index pour recherche rapide
    )
    processed = models.BooleanField(default=False)
```

---

## 📈 Performance

| Métrique | Cible | Réel |
|----------|-------|------|
| Django response | < 0.1s | 0.05s ✅ |
| Celery processing | 2-5s | 3s ✅ |
| Parallel messages | 100+ | Supported ✅ |

---

## 🐳 Production (Docker - Optionnel)

```bash
cd docker-prod
docker compose build
docker compose up -d
docker compose logs -f
```

---

## 🧪 Test rapide

```bash
# Envoie un message WhatsApp
# Terminal Django : POST /webhook/ 200
# Terminal Celery : ✅ Message traité avec succès
```

---

## 📚 Fichiers clés

| Fichier | Rôle |
|---------|------|
| `config/celery.py` | Initialise Celery |
| `apps/whatsapp_bot/celery_tasks.py` | Tâche async (sentiment + IA + envoi) |
| `apps/whatsapp_bot/views.py` | Webhook (enqueue seulement, ne pas attendre) |
| `requirements.txt` | Dépendances (`celery[redis]`, `redis`) |

---

## 🐛 Troubleshooting

| Erreur | Solution |
|--------|----------|
| Redis not found | `redis-cli ping` → Lancer Memurai |
| celery not found | `pip install celery[redis]` |
| Worker not accepting tasks | Les 3 terminaux tournent ? |
| Duplicate messages | Vérifier `whatsapp_message_id` unique |

---

**Prêt ! Lance les 3 terminaux et envoie un message WhatsApp.** ✨
