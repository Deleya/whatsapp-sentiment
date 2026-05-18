# 🤖 WORK.BAKETLI.TECH - Intelligent WhatsApp CRM Bot

🌍 *[Français ci-dessous](#-version-française)*

An AI-powered automated customer service system for WhatsApp, featuring a high-performance asynchronous architecture, local conversational sentiment analysis, and a B2B analytics dashboard.

## 🚀 Key Features
- **WhatsApp Cloud API Integration:** Real-time reception and sending of text messages and interactive menus.
- **AI Brain (Groq / LLaMA 3):** Ultra-fast contextual responses, adapted to the educational sector with a fallback system ensuring 100% uptime.
- **Global Sentiment Analysis (NLP):** Utilizes `DistilBERT Multilingual` locally to evaluate the customer's psychological state over the entire conversation (rather than sentence by sentence).
- **Tonal Adaptation:** The AI adjusts its empathy level based on the detected sentiment.
- **Automatic Escalation:** Instantly sends a WhatsApp alert to the administrator if a conversation escalates (negative global sentiment).
- **SaaS & CRM Dashboard:** Web interface powered by Tailwind CSS and Chart.js to visualize KPIs (global satisfaction rate, unique clients) and a Django Admin panel for CRM management.

## 🏗️ Technical Architecture
The application relies on strict decoupling to ensure maximum scalability (no dropped messages, even under heavy load):
- **Django (Backend):** Webhook entry point (response < 200ms) and database management (SQLite/PostgreSQL).
- **Celery + Redis:** Asynchronous queue (Broker & Worker) handling heavy external API calls (Groq, HuggingFace, Meta).

## ⚙️ Installation & Setup

**1. Environment Variables (`.env`)**
Create a `.env` file at the root:
```env
WHATSAPP_TOKEN=your_meta_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token
GROQ_API_KEY=your_groq_api_key
WHATSAPP_ADMIN_NUMBER=221xxxxxxxxx
```

**2. Starting the Services (Local Development)**
```bash
# 1. Ensure Redis is running
# Note: If using Docker on Windows, the backend engine (WSL/com.docker.backend) runs in the background and automatically starts Redis on boot, even if the Docker UI is closed!

# 2. Start the Django server
python manage.py runserver

# 3. Start the Celery worker (in a second terminal)
.\venv\Scripts\celery.exe -A config worker -l info --pool=solo
```

## 🛡️ Resilience
This project integrates production-level safety mechanisms:
- `try/except` blocks around all external API calls.
- HTTP Status Code validation with exponential retry strategies via Celery.
- Hardcoded fallback response dictionaries in case of a total LLM provider outage.

---

# 🇫🇷 Version Française

Un système de service client automatisé par IA (WhatsApp), doté d'une architecture asynchrone hautes performances, d'une analyse de sentiment conversationnelle locale, et d'un tableau de bord analytique B2B.

## 🚀 Fonctionnalités Principales
- **Intégration WhatsApp Cloud API :** Réception et envoi de messages textes et menus interactifs en temps réel.
- **Cerveau IA (Groq / LLaMA 3) :** Réponses contextuelles ultra-rapides, adaptées au domaine de la formation avec un système de "Fallbacks" pour assurer une disponibilité de 100%.
- **Analyse de Sentiment Globale (NLP) :** Utilisation de `DistilBERT Multilingual` en local pour évaluer l'état psychologique du client sur l'ensemble de la conversation (et non phrase par phrase).
- **Adaptation Tonale :** L'IA modifie son niveau d'empathie en fonction du sentiment détecté.
- **Escalade Automatique :** Envoi instantané d'une alerte WhatsApp à l'administrateur si une conversation dégénère (sentiment global négatif).
- **Dashboard SaaS & CRM :** Interface Web propulsée par Tailwind CSS et Chart.js pour visualiser les KPIs (taux de satisfaction global, clients uniques) et panel Admin Django pour la gestion CRM.

## 🏗️ Architecture Technique
L'application repose sur un découplage strict pour garantir une scalabilité maximale (aucune perte de message, même sous forte charge) :
- **Django (Backend) :** Point d'entrée Webhook (réponse < 200ms) et gestion de la base de données (SQLite/PostgreSQL).
- **Celery + Redis :** File d'attente asynchrone (Broker & Worker) gérant les appels API externes lourds (Groq, HuggingFace, Meta).

## ⚙️ Installation & Lancement

**1. Variables d'environnement (`.env`)**
Créez un fichier `.env` à la racine :
```env
WHATSAPP_TOKEN=your_meta_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token
GROQ_API_KEY=your_groq_api_key
WHATSAPP_ADMIN_NUMBER=221xxxxxxxxx
```

**2. Lancement des services (Développement Local)**
```bash
# 1. Vérifier que Redis tourne 
# Note : Si vous utilisez Docker sous Windows, le moteur (WSL/com.docker.backend) tourne en tâche de fond et relance souvent Redis de manière invisible au démarrage du PC, même si l'interface graphique Docker est fermée !

# 2. Lancer le serveur Django
python manage.py runserver

# 3. Lancer le worker Celery (dans un second terminal)
.\venv\Scripts\celery.exe -A config worker -l info --pool=solo
```

## 🛡️ Résilience
Ce projet intègre des sécurités de niveau production :
- `try/except` sur tous les appels APIs externes.
- Validation des Status Codes HTTP avec relance (Retry) exponentielle sur Celery.
- Dictionnaires de réponses de secours (Hardcoded) en cas de panne totale du fournisseur LLM.
