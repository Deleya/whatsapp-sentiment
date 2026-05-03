from transformers import pipeline

# 1. On charge un modèle spécialisé dans le sentiment (multilingue)
# Ce modèle donne une note de 1 à 5 étoiles (1 = très négatif, 5 = très positif)
print("Chargement du modèle d'IA... (Patientez, premier téléchargement)")
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
analyseur = pipeline("sentiment-analysis", model=model_name)

# 2. On crée une liste de phrases typiques que ton bot pourrait recevoir
phrases_tests = [
    "J'adore cette formation, c'est vraiment génial !",  # Positif
    "Je ne comprends rien à ce cours, c'est trop nul.",   # Négatif
    "Est-ce que vous pouvez me donner l'adresse ?",      # Neutre
    "C'est pas mal, mais un peu compliqué par moments."  # Mitigé
]

print("-" * 30)
print("RÉSULTATS DE L'ANALYSE :")
print("-" * 30)

# 3. On boucle sur les phrases pour voir ce que l'IA en pense
for phrase in phrases_tests:
    resultat = analyseur(phrase)[0]
    label = resultat['label']  # Exemple: '5 stars'
    score = resultat['score']  # Confiance de l'IA (entre 0 et 1)
    
    print(f"Texte : {phrase}")
    print(f"Verdict : {label} (Confiance : {score:.2f})")
    print("-" * 10)