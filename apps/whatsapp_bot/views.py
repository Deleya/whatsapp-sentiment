from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings
from .whatsapp_service import envoyer_alerte_whatsapp as envoyer_message_whatsapp
from .nlp_utils import analyser_message_whatsapp
from .agent_brain import generer_reponse
from .models import Message


def extract_message_data(webhook_data):
    """
    Extrait le numéro de téléphone, le texte du message et le type du webhook WhatsApp.
    Retourne un tuple (phone_number, message_text, message_type) ou (None, None, None) si extraction échouée.
    """
    try:
        entry = webhook_data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        # Vérifier si c'est un nouveau message
        if 'messages' not in value:
            return None, None, None

        message_obj = value['messages'][0]
        phone_number = message_obj.get('from')
        message_type = message_obj.get('type')

        if not phone_number:
            return None, None, None

        # Extraire le texte selon le type de message
        message_text = None

        if message_type == 'text':
            message_text = message_obj.get('text', {}).get('body', '')

        elif message_type == 'image':
            # Récupérer la légende si elle existe
            message_text = message_obj.get('image', {}).get('caption')
            if not message_text:
                message_text = "[Image reçue sans légende]"

        elif message_type == 'video':
            message_text = message_obj.get('video', {}).get('caption')
            if not message_text:
                message_text = "[Vidéo reçue sans légende]"

        elif message_type == 'audio':
            message_text = "[Message audio reçu]"

        elif message_type == 'document':
            # Récupérer le nom du document si possible
            filename = message_obj.get('document', {}).get('filename', 'document')
            message_text = f"[Document reçu: {filename}]"

        elif message_type == 'location':
            message_text = "[Localisation reçue]"

        else:
            message_text = f"[Type de message non géré: {message_type}]"

        return phone_number, message_text if message_text else "", message_type

    except (KeyError, IndexError, TypeError) as e:
        print(f"❌ Erreur lors de l'extraction du message: {e}")
        return None, None, None


@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request):
    print(f"\n{'='*90}")
    print(f"REQUÊTE REÇUE - Méthode: {request.method} | Path: {request.path}")
    print(f"{'='*90}")

    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        print(f"GET - Verify Token reçu: {token}")

        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            print("✅ Webhook vérifié avec succès par Meta !")
            return JsonResponse(int(challenge), safe=False, status=200)
        
        print("❌ Verify token invalide")
        return JsonResponse({"error": "Invalid verify token"}, status=403)

    # === POST ===
    try:
        data = json.loads(request.body)
        print("✅ POST REÇU AVEC SUCCÈS !")
        print("Payload complet reçu :")
        print(json.dumps(data, indent=2))

        # Extraire les données du message
        phone_number, message_text, message_type = extract_message_data(data)

        if phone_number and message_text:
            sentiment_label = None
            sentiment_score = None

            # Analyse IA pour les messages texte
            if message_type == 'text':
                try:
                    resultat_ia = analyser_message_whatsapp(message_text)
                    sentiment_label = resultat_ia['label']  # positive, negative ou neutral
                    sentiment_score = resultat_ia['score']

                    print(f"--- ANALYSE IA RÉUSSIE ---")
                    print(f"Message : {message_text}")
                    print(f"Sentiment : {sentiment_label} ({sentiment_score})")
                    print(f"------------------------")
                except Exception as e:
                    print(f"⚠️  Erreur lors de l'analyse IA : {e}")

            # Sauvegarde dans la base
            message_obj = Message.objects.create(
                phone_number=phone_number,
                message_text=message_text,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score,
                raw_webhook_data=data,
                processed=True if sentiment_label else False
            )
            print(f"✅ Message sauvegardé !")
            print(f"   Numéro: {phone_number}")
            print(f"   Texte: {message_text[:100]}...")
            if sentiment_label:
                print(f"   Sentiment: {sentiment_label} ({sentiment_score})")
            print(f"   ID: {message_obj.id}")

            # ============================================================
            # AUTOMATISATION : Réponse IA + alerte admin si négatif
            # ============================================================

            # Alerte admin si message négatif
            if sentiment_label and sentiment_label.upper() in ('NEGATIVE', 'NÉGATIF', 'NEGATIF'):
                alerte = (
                    f"⚠️ MÉCONTENT : {phone_number} a dit :\n"
                    f"'{message_text}'"
                )
                try:
                    envoyer_message_whatsapp(alerte, "221776746609")
                    print(">>> ✅ Alerte admin envoyée !")
                except Exception as e:
                    print(f"❌ Erreur alerte admin : {e}")

            # Générer la réponse IA via Groq/LLaMA 3
            reponse = generer_reponse(
                message_utilisateur=message_text,
                numero_tel=phone_number,
                sentiment=sentiment_label,
                score=sentiment_score
            )

            # 3. Envoi de la réponse à l'utilisateur (AUTOMATIQUE)
            try:
                envoyer_message_whatsapp(reponse, phone_number)
                print(f">>> ✅ Réponse auto envoyée à {phone_number} : {reponse}")
            except Exception as e:
                print(f"❌ Erreur envoi réponse user : {e}")

        else:
            print("⚠️  Aucun message à traiter (webhook reçu mais pas de données de message)")

        print(f"{'='*90}\n")
        return JsonResponse({"status": "success"}, status=200)

    except json.JSONDecodeError:
        print("❌ Erreur : Le body n'est pas du JSON valide")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return JsonResponse({"error": "Server error"}, status=500)


def dashboard(request):
    total = Message.objects.count()

    # Nombre d'utilisateurs uniques (numéros de téléphone distincts)
    nb_utilisateurs = Message.objects.values('phone_number').distinct().count()

    nb_positifs = Message.objects.filter(sentiment_label='positive').count()
    nb_negatifs = Message.objects.filter(sentiment_label='negative').count()
    nb_neutres = Message.objects.filter(sentiment_label='neutral').count()

    # Messages non encore analysés (sentiment_label est NULL)
    nb_pending = Message.objects.filter(sentiment_label__isnull=True).count()

    # Les pourcentages sont calculés sur les messages ANALYSÉS uniquement
    nb_analyses = nb_positifs + nb_negatifs + nb_neutres

    if nb_analyses > 0:
        pourcent_positif = (nb_positifs / nb_analyses) * 100
        pourcent_negatif = (nb_negatifs / nb_analyses) * 100
        pourcent_neutre = (nb_neutres / nb_analyses) * 100
    else:
        pourcent_positif = pourcent_negatif = pourcent_neutre = 0

    context = {
        'total': total,
        'positifs': nb_positifs,
        'negatifs': nb_negatifs,
        'neutres': nb_neutres,
        'pending': nb_pending,
        'nb_analyses': nb_analyses,
        'utilisateurs': nb_utilisateurs,
        'p_positif': round(pourcent_positif, 1),
        'p_negatif': round(pourcent_negatif, 1),
        'p_neutre': round(pourcent_neutre, 1),
    }

    return render(request, 'whatsapp_bot/dashboard.html', context)