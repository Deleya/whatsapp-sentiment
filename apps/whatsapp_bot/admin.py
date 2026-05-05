from django.contrib import admin
from django.utils.html import format_html, mark_safe
import json

from django.db.models import OuterRef, Subquery
from .models import Message, ClientSatisfaction


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'get_message_text', 'colored_sentiment', 'sentiment_bar', 'timestamp')
    list_filter = ('sentiment_label', 'timestamp', 'processed')
    readonly_fields = ('raw_webhook_data',)

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                ('Informations du message', {
                    'fields': ('phone_number', 'message_text', 'timestamp')
                }),
                ('Analyse Sentiment', {
                    'fields': ('colored_sentiment_detail', 'sentiment_bar_detail', 'processed'),
                    'classes': ('wide',)
                }),
                ('Données brutes (Debug)', {
                    'fields': ('raw_webhook_data',),
                    'classes': ('collapse',)
                }),
            )
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return list(self.readonly_fields) + ['colored_sentiment_detail', 'sentiment_bar_detail']
        return self.readonly_fields

    def get_message_text(self, obj):
        text = obj.message_text[:50] + "..." if len(obj.message_text) > 50 else obj.message_text
        return text
    get_message_text.short_description = "Message"

    def colored_sentiment(self, obj):
        """Affiche le sentiment avec couleur dans la liste"""
        if not obj.sentiment_label:
            return mark_safe('<span style="color: grey;">Non analysé</span>')

        color = {
            'positive': '#28a745',   # Vert
            'negative': '#dc3545',   # Rouge
            'neutral': '#ffc107'      # Jaune
        }.get(obj.sentiment_label, 'grey')

        return format_html(
            '<b style="color: {}; font-size: 13px;">{}</b>',
            color,
            obj.sentiment_label
        )
    colored_sentiment.short_description = 'Sentiment'

    def colored_sentiment_detail(self, obj):
        """Affiche le sentiment avec couleur en détail"""
        if not obj.sentiment_label:
            return mark_safe('<span style="color: grey; font-size: 16px;">Non analysé</span>')

        color = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#ffc107'
        }.get(obj.sentiment_label, 'grey')

        emoji = {
            'positive': '😊',
            'negative': '😞',
            'neutral': '😐'
        }.get(obj.sentiment_label, '')

        return format_html(
            '<h3 style="color: {};">{} {}</h3>',
            color,
            emoji,
            obj.sentiment_label
        )
    colored_sentiment_detail.short_description = 'Sentiment Analysé'

    def sentiment_bar(self, obj):
        """Barre de confiance minimaliste pour la liste"""
        if not obj.sentiment_score:
            return "—"

        percentage = int(obj.sentiment_score * 100)
        bar_color = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#ffc107'
        }.get(obj.sentiment_label, '#999')

        return format_html(
            '<div style="width: 80px; height: 8px; background-color: #eee; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background-color: {}; transition: width 0.3s;"></div>'
            '</div>',
            percentage,
            bar_color
        )
    sentiment_bar.short_description = 'Confiance'

    def sentiment_bar_detail(self, obj):
        """Barre de confiance détaillée pour la vue détail"""
        if not obj.sentiment_score:
            return mark_safe('<span style="color: grey;">Pas de score</span>')

        percentage = int(obj.sentiment_score * 100)
        bar_color = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#ffc107'
        }.get(obj.sentiment_label, '#999')

        return format_html(
            '<div style="margin: 20px 0;">'
            '<div style="width: 100%; max-width: 400px; height: 30px; background-color: #f0f0f0; border-radius: 6px; overflow: hidden; border: 2px solid {color};">'
            '<div style="width: {percentage}%; height: 100%; background-color: {color}; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: bold;"></div>'
            '</div>'
            '<p style="margin-top: 10px; font-size: 16px;"><strong>Confiance: {percentage}%</strong></p>'
            '</div>',
            color=bar_color,
            percentage=percentage
        )
    sentiment_bar_detail.short_description = 'Barre de Confiance'

@admin.register(ClientSatisfaction)
class ClientSatisfactionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'colored_sentiment', 'sentiment_bar', 'timestamp')
    list_filter = ('sentiment_label',)
    search_fields = ('phone_number',)
    
    # Empêcher d'ajouter ou de supprimer manuellement depuis cette vue (c'est un tableau de bord)
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # SQLite compatible: On filtre pour n'obtenir que le message le plus récent par numéro
        latest_messages = Message.objects.filter(
            phone_number=OuterRef('phone_number')
        ).order_by('-timestamp')
        
        return qs.filter(id=Subquery(latest_messages.values('id')[:1]))

    def colored_sentiment(self, obj):
        if not obj.sentiment_label:
            return mark_safe('<span style="color: grey;">Non analysé</span>')

        color = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#ffc107'
        }.get(obj.sentiment_label, 'grey')

        return format_html(
            '<b style="color: {}; font-size: 14px;">{}</b>',
            color,
            obj.sentiment_label.upper()
        )
    colored_sentiment.short_description = 'État Final du Client'

    def sentiment_bar(self, obj):
        if not obj.sentiment_score:
            return "—"

        percentage = int(obj.sentiment_score * 100)
        bar_color = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#ffc107'
        }.get(obj.sentiment_label, '#999')

        return format_html(
            '<div style="width: 100px; height: 8px; background-color: #eee; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background-color: {}; transition: width 0.3s;"></div>'
            '</div>',
            percentage,
            bar_color
        )
    sentiment_bar.short_description = 'Confiance IA'
