from transformers import pipeline

# On charge le modèle une seule fois ici (au chargement du fichier)
# pour éviter de le recharger à chaque message reçu.
print("Chargement de l'IA de sentiment...")
# On utilise DistilBERT multilingue, qui est conversationnel, très rapide et ne nécessite pas SentencePiece
analyseur = pipeline("sentiment-analysis", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")

def analyser_message_whatsapp(texte):
    """
    Cette fonction prend un texte et retourne un dictionnaire 
    avec le sentiment simplifié et le score.
    """
    # 1. On demande à l'IA d'analyser le texte
    resultat_brut = analyseur(texte)[0]
    
    label_ia = resultat_brut['label'].lower()  # Le modèle renvoie souvent 'negative', 'neutral', 'positive'
    score_ia = resultat_brut['score']
    
    # 2. On prépare notre variable de réponse
    sentiment_final = "neutral"
    
    # 3. La logique de traduction
    # Ce modèle est beaucoup plus précis pour les messages courts. 
    # On lui fait confiance même si le score est moyen.
    
    if label_ia in ['negative', 'label_0']:
        sentiment_final = "negative"
        
    elif label_ia in ['positive', 'label_2']:
        sentiment_final = "positive"
        
    else:
        sentiment_final = "neutral"

    # 4. On renvoie un dictionnaire propre pour Django
    return {
        'label': sentiment_final,
        'score': round(score_ia, 2) # On arrondit à 2 chiffres (ex: 0.85)
    }