from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings

from .models import Message


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

        # Sauvegarde dans la base
        message_obj = Message.objects.create(
            phone_number="PENDING",
            message_text="Message reçu (raw)",
            raw_webhook_data=data,
            processed=False
        )

        print(f"✅ Message sauvegardé dans la base de données ! ID = {message_obj.id}")
        print(f"{'='*90}\n")

        return JsonResponse({"status": "success"}, status=200)

    except json.JSONDecodeError:
        print("❌ Erreur : Le body n'est pas du JSON valide")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return JsonResponse({"error": "Server error"}, status=500)