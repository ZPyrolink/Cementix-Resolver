from gensim.models import KeyedVectors
import random
import requests
import threading

FIRST_WORDS = "courage"
SCORES = {}
DICO = 'frWracOnlyWord.bin'

def sendWord(word):
    # URL de l'API à laquelle vous voulez envoyer la requête POST
    url = "	https://cemantix.certitudes.org/score"

    # Données à envoyer en JSON
    data = {
        "word": word,
    }

    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://cemantix.certitudes.org/",
        "Origin": "https://cemantix.certitudes.org",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "DNT": "1",
        "Sec-GPC": "1"
    }

    # Effectuer la requête POST
    response = requests.post(url, data=data, headers=headers)

    try :
        return response.json()["score"]
    except :
        return 0

# Fonction pour calculer le score d'un mot en utilisant un thread
def calculer_score(word: str, generation: int):
    """
    Fonction des threads pour calculer le score d'un mot
    :param word: Mot à évaluer
    :param generation: Génération du mot
    :return: None
    """
    score = sendWord(word)
    if generation not in SCORES:
        SCORES[generation] = {}
    SCORES[generation][word] = score  # Enregistre le score dans le dictionnaire spécifique à la génération

def getNextGen(word,model,gen):
    """
    Récupère les scores de la génération suivante
    :param word: Le meilleurs mot de la génération précédente
    :param model: Le modèle contenant les mots
    :param gen: Le numéro de la génération
    :return: Le dictionnaire des scores de la génération gen
    """

    # Trouve le mots les plus similaires
    vector = model.most_similar(word)

    # Transforme les mots les plus similaires en une liste de mots
    words = [word for word, _ in vector]

    # Crée un thread pour chaque mot
    threads = []
    for mot in words:
        t = threading.Thread(target=calculer_score, args=(mot, gen))
        threads.append(t)
        t.start()

    # Attend la fin de tous les threads
    for t in threads:
        t.join()

    return SCORES[gen]

def getBestWord(score_gen):
    """
    Récupère le mot avec le meilleur score
    :param score_gen: Dictionnaire des scores de la dernière génération
    :return: Un tuple contenant le mot avec le meilleur score et le score
    """
    best_word = ""
    best_score = 0
    for word, score in score_gen.items():
        if score > best_score:
            best_score = score
            best_word = word
    return best_word,best_score

def main():
    # Load pre-trained Word2Vec model
    model = KeyedVectors.load_word2vec_format(DICO, binary=True, unicode_errors="ignore")

    precBestWord = [FIRST_WORDS]
    #On initialise la première génération
    gen = 0
    score_gen = getNextGen(FIRST_WORDS,model,gen)
    best_word,best_score = getBestWord(score_gen)

    #On boucle tant que le meilleur score n'est pas 1
    while best_score != 1:
        print(best_word,best_score)
        gen += 1
        score_gen = getNextGen(best_word,model,gen)
        best_word,best_score = getBestWord(score_gen)
        precBestWord.append(best_word)
        if best_word in precBestWord[:-1] or best_score == 0:
            best_word = random.choice(model.index_to_key)


if __name__ == "__main__":
    main()