from django.contrib import admin
import json

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    # On affiche les colonnes importantes et lisibles
    list_display = ('phone_number', 'get_message_text', 'sentiment_label', 'sentiment_score', 'timestamp')
    
    # On permet de filtrer par sentiment ou par date
    list_filter = ('sentiment_label', 'timestamp')
    
    # On rend le champ brut lisible seulement dans la vue détaillée (quand on clique sur le message)
    readonly_fields = ('raw_webhook_data',)

    # Petite méthode magique pour extraire le texte du message du JSON pour le tableau
    def get_message_text(self, obj):
        try:
            # raw_webhook_data est déjà un dict, pas besoin de json.loads
            data = obj.raw_webhook_data
            return data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'][:50] + "..."
        except (KeyError, IndexError, TypeError):
            return "Texte indisponible"
    
    get_message_text.short_description = "Message (extrait)" # Nom de la colonne
