import requests
from django.conf import settings


def send_whatsapp_message(phone_number, message_text):
    """
    Envoie un message WhatsApp via l'API Meta.
    """
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ Erreur envoi WhatsApp: {e}")
        return {"error": str(e)}

def envoyer_boutons_amorce(phone_number):
    """
    Envoie un menu interactif avec 3 boutons pour guider l'utilisateur.
    """
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Bienvenue chez WORK.BAKETLI.TECH ! ✨\nComment puis-je vous accompagner aujourd'hui ?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "btn_formations", "title": "Nos Formations 📚"}
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "btn_expert", "title": "Parler à un expert 👤"}
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "btn_ia", "title": "Infos sur l'IA 🤖"}
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ Erreur envoi boutons WhatsApp: {e}")
        return {"error": str(e)}
