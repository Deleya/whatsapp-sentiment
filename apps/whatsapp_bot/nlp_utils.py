from transformers import pipeline
import re

# On charge le modèle une seule fois ici (au chargement du fichier)
# pour éviter de le recharger à chaque message reçu.
print("Chargement de l'IA de sentiment...")
# On utilise DistilBERT multilingue, qui est conversationnel, très rapide et ne nécessite pas SentencePiece
analyseur = pipeline("sentiment-analysis", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")

# ===================================================================
# DICTIONNAIRE DE MOTS-CLÉS NÉGATIFS (Français informel + formel)
# Le modèle DistilBERT est faible sur le français familier.
# Cette couche "humaine" corrige ses erreurs les plus grossières.
# ===================================================================
MOTS_NEGATIFS = [
    # Mécontentement direct
    'nul', 'nulle', 'nuls', 'nulles',
    'mauvais', 'mauvaise', 'horrible', 'horreur',
    'mécontent', 'mécontente', 'déçu', 'déçue', 'déception',
    'arnaque', 'arnaquer', 'voleur', 'voleurs',
    'scandale', 'scandaleux', 'honteux', 'honte',
    'inacceptable', 'inadmissible',
    # Frustration
    'ras le bol', 'marre', 'j\'en ai marre', 'ça suffit',
    'n\'importe quoi', 'nimporte quoi', 'ridicule',
    'perte de temps', 'inutile',
    # Insultes légères
    'incompétent', 'incompétente', 'incompétents',
    # Départ / abandon
    'bye', 'au revoir', 'adieu', 'je pars', 'je m\'en vais',
    'pas ce que je cherche', 'pas ce que je veux',
    'pas intéressé', 'pas interessé', 'pas intéressée',
    'ne répond pas', 'ne marche pas', 'ça marche pas',
    'pas satisfait', 'pas satisfaite',
    # Négation forte
    'jamais', 'aucun', 'aucune',
    'je déteste', 'je hais', 'dégueulasse', 'dégoûté',
    # Anglais courant
    'trash', 'garbage', 'useless', 'worst', 'terrible', 'awful', 'sucks',
    'bad', 'disappointed', 'angry', 'hate',
]

# Pré-compiler le pattern regex pour la performance
# On utilise des word boundaries (\b) pour éviter les faux positifs
PATTERN_NEGATIF = re.compile(
    r'\b(' + '|'.join(re.escape(mot) for mot in MOTS_NEGATIFS) + r')\b',
    re.IGNORECASE
)


def detecter_negativite_par_mots_cles(texte):
    """
    Détecte la négativité par mots-clés dans le texte.
    Retourne (True, [mots trouvés]) si négatif, (False, []) sinon.
    """
    texte_normalise = texte.lower().strip()
    mots_trouves = PATTERN_NEGATIF.findall(texte_normalise)
    return (len(mots_trouves) > 0, mots_trouves)


def analyser_message_whatsapp(texte):
    """
    Analyse le sentiment d'un SEUL message.
    Combine le modèle IA + la détection par mots-clés.
    """
    # 1. Détection par mots-clés (prioritaire sur le modèle)
    est_negatif, mots = detecter_negativite_par_mots_cles(texte)
    
    # 2. Analyse par le modèle IA
    resultat_brut = analyseur(texte)[0]
    label_ia = resultat_brut['label'].lower()
    score_ia = resultat_brut['score']
    
    # 3. Logique de décision
    if est_negatif:
        # Les mots-clés l'emportent : c'est clairement négatif
        sentiment_final = "negative"
        score_final = max(score_ia, 0.85)  # Score minimum de 0.85 pour les mots-clés
        print(f"    🔑 Mots-clés négatifs détectés: {mots} → Forçage négatif")
    elif label_ia in ['negative', 'label_0']:
        sentiment_final = "negative"
        score_final = score_ia
    elif label_ia in ['positive', 'label_2']:
        sentiment_final = "positive"
        score_final = score_ia
    else:
        sentiment_final = "neutral"
        score_final = score_ia

    return {
        'label': sentiment_final,
        'score': round(score_final, 2)
    }


def analyser_sentiment_global(messages_textes):
    """
    Analyse le sentiment GLOBAL d'une conversation complète.
    
    Prend une liste de textes (les N derniers messages du client)
    et retourne le sentiment dominant de la conversation.
    
    Logique :
    - On analyse chaque message individuellement (IA + mots-clés)
    - On compte les votes : positive / neutral / negative
    - On pondère les messages récents plus fortement (les derniers comptent double)
    - Si au moins un message récent (les 2 derniers) est négatif, on considère la conversation négative
      (principe de précaution : un client mécontent en fin de conversation = alerte)
    """
    if not messages_textes:
        return {'label': 'neutral', 'score': 0.5}
    
    # Analyser chaque message
    resultats = []
    for texte in messages_textes:
        try:
            r = analyser_message_whatsapp(texte)
            resultats.append(r)
        except Exception:
            resultats.append({'label': 'neutral', 'score': 0.5})
    
    # Comptage des sentiments
    compteur = {'positive': 0, 'neutral': 0, 'negative': 0}
    scores = {'positive': [], 'neutral': [], 'negative': []}
    
    for r in resultats:
        compteur[r['label']] += 1
        scores[r['label']].append(r['score'])
    
    # Pondération : les 2 derniers messages comptent double
    nb_messages = len(resultats)
    if nb_messages >= 2:
        for r in resultats[-2:]:
            compteur[r['label']] += 1  # Vote bonus pour les messages récents
    
    # Principe de précaution : si un des 2 derniers messages est négatif → alerte
    messages_recents = resultats[-2:] if nb_messages >= 2 else resultats
    negatif_recent = any(r['label'] == 'negative' for r in messages_recents)
    
    if negatif_recent:
        sentiment_global = 'negative'
        score_moyen = sum(scores.get('negative', [0.5])) / max(len(scores.get('negative', [1])), 1)
    else:
        # Sinon, on prend le sentiment majoritaire
        sentiment_global = max(compteur, key=compteur.get)
        score_moyen = sum(scores.get(sentiment_global, [0.5])) / max(len(scores.get(sentiment_global, [1])), 1)
    
    print(f"📊 Analyse globale — Votes: {compteur} | Négatif récent: {negatif_recent} → Résultat: {sentiment_global}")
    
    return {
        'label': sentiment_global,
        'score': round(score_moyen, 2)
    }