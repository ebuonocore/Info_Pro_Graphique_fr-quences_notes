""" Graphiques de répartition de notes
    le 04/12/2021 par Eric Buonocore
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle
import requests # Appel de l'API de github
import json # Conversion des enregistrements au format JSON
import base64 # Décodage de la requête

class Evaluation():
    def __init__(self, évaluation):
        self.désignation = évaluation["Désignation"]
        self.barème = évaluation["Barème"]
        self.notes = évaluation["Notes"]
        # Notes normalisées: Ramenées sur 20
        self.notes_normalisées = list(map(lambda x:x*20/self.barème, self.notes))
        self.écart_type = np.std(self.notes_normalisées)
        self.intervales = [0] * 21
        self.hauteur_max = 0
        self.maj_intervales()

    def maj_intervales(self):
        """ Affection dans chaque intervale du nombre de notes correspondantes
        """
        for note in self.notes_normalisées:
            indice = int(note)
            self.intervales[indice] +=1
            self.hauteur_max = max(self.hauteur_max, self.intervales[indice])

class Graphique_barres:
    def __init__(self, évaluations):
        self.ind = 0 # Indice de l'évaluation à afficher
        self.évaluations = évaluations # Liste des séries de données : nombre de notes par intervale
        # Valeurs de l'axe des abscisses
        self.X = [x for x in range(0,21)]
        self.couleurs = ['#33aa33','#33bb33','#22cc22','#11cc22','#00dd00']

    def affiche(self):
        """ Trace le graphique en barres de l'évaluation d'indice self.indice
        """
        ax.clear() # Nettoyage des graphiques précédents
        nb_evals = len(self.évaluations)
        i = self.ind % nb_evals
        intervales = self.évaluations[i].intervales
        notes_20 = self.évaluations[i].notes_normalisées
        moyenne = sum(notes_20)//len(notes_20)
        écart = self.évaluations[i].écart_type
        moyenne_plus = moyenne +  self.évaluations[i].écart_type
        hauteur = self.évaluations[i].hauteur_max
        ax.add_patch(Rectangle((moyenne - écart, 0), 2 * écart, hauteur, color = '#eeffee'))
        couleur = self.couleurs[i%len(self.couleurs)]
        ax.bar(self.X, intervales, color = couleur) # Trace le graphique en barres
        ax.set_title(self.évaluations[i].désignation + '/' + str(nb_evals)) # Renomme le graphique
        # Calcul et affiche la moyenne des notes
        ax.axvline(moyenne,0,1,color='lime')
        plt.draw()

    def suivant(self, event):
        """ Appui sur le bouton suivant
        """
        self.ind += 1
        self.affiche()

    def précédent(self, event):
        """ Appui sur le bouton précédent
        """
        self.ind -= 1
        self.affiche()


# Récupération des évaluations sauvegardées sur github au format json
source = 'https://api.github.com/repos/ebuonocore/Info_Pro_Graphique_frequences_notes/contents/20211203_serie_notes.json'
print("Ouverture du fichier: ", source)
req = requests.get(source)
if req.status_code == 200:
    req = req.json()
    content = base64.b64decode(req['content'])
else:
    print('Le fichier n\'a pas été trouvé')
relevés = json.loads(content.decode('utf-8'))['Evaluations']

print("Traitement des données")
évaluations = [] # Agrégateurs des instances de type Evaluation
for relevé in relevés:
    évaluations.append( Evaluation(relevé))

# Création de la figure pour dessiner les graphiques: 2 boutons > et < permettent la navigation
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)

callback = Graphique_barres(évaluations)
axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
bnext = Button(axnext, '>')
bnext.on_clicked(callback.suivant)
bprev = Button(axprev, '<')
bprev.on_clicked(callback.précédent)

callback.affiche()
plt.show()

plt.close(fig) # Libère la mémoire prise par la figure