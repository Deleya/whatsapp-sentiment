from celery import shared_task
from .nlp_utils import analyser_message_whatsapp
from .agent_brain import generer_reponse
from .whatsapp_sender import send_whatsapp_message, envoyer_boutons_amorce
from .whatsapp_service import envoyer_alerte_whatsapp
from .models import Message


@shared_task(bind=True, max_retries=3, acks_late=True)
def process_message_async(self, phone_number, message_text, message_type, message_id, raw_webhook_data):
    """
    Tâche async: Analyse sentiment + génère réponse + envoie WhatsApp.

    Args:
        phone_number: Numéro WhatsApp du client
        message_text: Texte du message
        message_type: Type (text, image, video, etc.)
        message_id: UUID du message en DB
        raw_webhook_data: Données brutes du webhook
    """
    try:
        sentiment_label = None
        sentiment_score = None

        print(f"🔄 Traitement async commencé: {phone_number}")

        # 0. Vérifier si le message a déjà été traité
        message_obj = Message.objects.filter(id=message_id).first()
        if not message_obj:
            print(f"❌ Message introuvable au moment du traitement: {message_id}")
            return
        if message_obj.processed:
            print(f"⚠️  Message déjà traité: {message_id}")
            return

        # 0.5. Amorce de discussion (Menu interactif)
        mots_amorce = ['bonjour', 'salut', 'hello', 'menu', 'aide', 'coucou', 'start']
        if message_type == 'text' and message_text.lower().strip() in mots_amorce:
            print(f"👋 Amorce détectée, envoi du menu interactif à {phone_number}")
            try:
                envoyer_boutons_amorce(phone_number)
            except Exception as e:
                print(f"❌ Erreur envoi amorce: {e}")
            
            # On met à jour la base de données comme "traité"
            try:
                message_obj = Message.objects.get(id=message_id)
                message_obj.processed = True
                message_obj.save()
            except:
                pass
            return # On s'arrête là, pas besoin de Groq pour un simple "bonjour"

        # 1. Analyser sentiment (seulement pour les textes ou clics de boutons)
        if message_type in ['text', 'interactive']:
            try:
                # LOGIQUE METIER : Analyse globale de la conversation
                # On récupère les 4 derniers messages du client pour comprendre son évolution
                derniers_msgs = Message.objects.filter(
                    phone_number=phone_number
                ).exclude(message_text="").order_by('-timestamp')[:4]
                
                # On remet les messages dans l'ordre chronologique (du plus ancien au plus récent)
                textes = [msg.message_text for msg in derniers_msgs]
                textes.reverse()
                
                # On assemble le tout pour nourrir l'IA de Sentiment
                contexte_global = " | ".join(textes)
                print(f"🔍 Contexte global envoyé à l'IA : {contexte_global}")
                
                resultat_ia = analyser_message_whatsapp(contexte_global)
                sentiment_label = resultat_ia['label']
                sentiment_score = resultat_ia['score']
                print(f"📊 Sentiment global analysé: {sentiment_label} ({sentiment_score})")
            except Exception as e:
                print(f"❌ Erreur Sentiment Analysis: {e}. Valeurs par défaut appliquées.")
                sentiment_label = "neutral"
                sentiment_score = 0.5

        # 2. Générer réponse IA
        reponse_ia = generer_reponse(
            message_utilisateur=message_text,
            numero_tel=phone_number,
            sentiment=sentiment_label,
            score=sentiment_score
        )
        print(f"🧠 Réponse IA générée: {len(reponse_ia)} chars")

        # 3. Envoyer réponse WhatsApp
        if reponse_ia:
            try:
                result = send_whatsapp_message(phone_number, reponse_ia)
                print(f"📤 Message WhatsApp envoyé: {result}")
            except Exception as e:
                print(f"❌ Impossible d'envoyer le WhatsApp final: {e}")

        # 3.5. Alerte Admin si sentiment négatif
        if sentiment_label == 'negative':
            try:
                # Bonne pratique : On récupère le numéro depuis le fichier .env
                from decouple import config
                admin_number = config("WHATSAPP_ADMIN_NUMBER", default="221776746609")
                
                message_alerte = f"⚠️ *ALERTE CLIENT MÉCONTENT*\nNuméro: {phone_number}\nMessage: {message_text}"
                envoyer_alerte_whatsapp(message_alerte, admin_number)
                print(f"🚨 Alerte Admin envoyée pour le numéro {phone_number} à l'admin {admin_number}")
            except Exception as e:
                print(f"❌ Impossible d'envoyer l'alerte Admin: {e}")

        # 4. Mettre à jour le message en DB
        try:
            message_obj = Message.objects.get(id=message_id)
            message_obj.sentiment_label = sentiment_label
            message_obj.sentiment_score = sentiment_score
            message_obj.processed = True
            message_obj.save()
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde en DB: {e}")

        print(f"✅ Message traité avec succès: {phone_number}")

    except Message.DoesNotExist:
        print(f"❌ Message non trouvé: {message_id}")
    except Exception as e:
        print(f"❌ Erreur traitement async: {e}")
        # Retry avec backoff exponentiel (3s, 6s, 12s)
        try:
            self.retry(exc=e, countdown=3 ** self.request.retries)
        except Exception as retry_e:
            print(f"❌ Retry échoué: {retry_e}")
            # Marquer comme erreur en DB
            try:
                message_obj = Message.objects.get(id=message_id)
                message_obj.processed = False
                message_obj.save()
            except:
                pass
