from transformers import pipeline

# On charge le modèle une seule fois ici (au chargement du fichier)
# pour éviter de le recharger à chaque message reçu.
print("Chargement de l'IA...")
analyseur = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def analyser_message_whatsapp(texte):
    """
    Cette fonction prend un texte et retourne un dictionnaire 
    avec le sentiment simplifié et le score.
    """
    # 1. On demande à l'IA d'analyser le texte
    resultat_brut = analyseur(texte)[0]
    
    label_ia = resultat_brut['label']  # ex: '5 stars'
    score_ia = resultat_brut['score']  # ex: 0.95
    
    # 2. On prépare notre variable de réponse
    sentiment_final = "neutral" # Par défaut (correspond aux choices du modèle Django)
    
    # 3. La logique de traduction (Le coeur du code)
    
    # Sécurité : si l'IA hésite trop, on reste sur Neutre
    if score_ia < 0.4:
        sentiment_final = "neutral"
    
    # Sinon, on traduit les étoiles
    elif label_ia in ['4 stars', '5 stars']:
        sentiment_final = "positive"
        
    elif label_ia in ['1 star', '2 stars']:
        sentiment_final = "negative"
        
    else:
        sentiment_final = "neutral"

    # 4. On renvoie un dictionnaire propre pour Django
    return {
        'label': sentiment_final,
        'score': round(score_ia, 2) # On arrondit à 2 chiffres (ex: 0.85)
    }