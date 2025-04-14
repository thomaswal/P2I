# IA Deep Q-Learning pour le Jeu de Dames

Ce projet implémente une intelligence artificielle utilisant l'apprentissage par renforcement (Deep Q-Learning) pour jouer au jeu de dames. L'IA apprend en jouant contre elle-même et s'améliore progressivement.


## Structure du Projet

Le projet est composé des fichiers suivants :

- `Plateau.py` : Classe gérant la logique du jeu de dames (déplacements, éliminations, etc.)
- `DamesJoueurvsJoueur.py` : Interface graphique du jeu utilisant Tkinter joueur contre joueur
- `DamesJoueurvsIA.py` : Interface graphique du jeu utilisant Tkinter joueur contre IA
- `IA_DQN.py` : Implémentation du modèle Deep Q-Learning et de l'agent d'apprentissage
- `EntrainementIA.py` : Gestion du lancement de l'entrainement de l'IA


## Utilisation

### Jouer contre l'IA

Pour jouer contre l'IA entraînée lancer le fichier DamesJoueurvsIA.py

```python
python DamesJoueurvsIA.py
```
### Jouer contre un autre joueur

Pour jouer contre un autre joueur lancer le fichier DamesJoueurvsJoueur.py

```python
python DamesJoueursvIA.py
```

### Entraînement du Modèle

Pour entraîner le modèle lancer le fichier EntrainementIA.py

```python
python EntrainementIA.py
```

Ce fichier utilise la fonction `train_self_play()` du fichier `IA_DQN.py` :


### Optimisation des Paramètres

Pour optimiser les hyperparamètres du modèle, utilisez le script `optimisation_parametres.py` :

```python
python optimisation_parametres.py
```

Ce script testera différentes combinaisons de taux d'apprentissage, facteur de réduction gamma et taux de décroissance d'epsilon, et identifiera les meilleurs paramètres.


## Fonctionnement du Modèle Deep Q-Learning

### Hyperparamètres

Vous pouvez personnaliser les hyperparamètres lors de la création de l'agent :

```python
agent = IA_DQN(
    learning_rate=0.001,  # Taux d'apprentissage
    gamma=0.95,           # Facteur de réduction pour les récompenses futures
    epsilon=1.0,          # Paramètre d'exploration initial
    epsilon_min=0.01,     # Valeur minimale d'epsilon
    epsilon_decay=0.995,  # Facteur de décroissance d'epsilon
    memory_size=10000     # Taille de la mémoire de replay
)
```

### Représentation de l'État

L'état du jeu est représenté par une liste de 50 cases jouables (l'index 0 n'est pas utilisé). Chaque case peut contenir :
- `None` pour une case vide
- Un tuple `(joueur, est_dame)` où `joueur` est 0 ou 1 et `est_dame` est un booléen

Pour le réseau neuronal, cet état est prétraité en un tableau de 50 valeurs où :
- 0 représente une case vide
- 1 représente un pion du joueur 1
- -1 représente un pion du joueur 0
- 2 représente une dame du joueur 1
- -2 représente une dame du joueur 0

### Structure des Actions

Les actions sont représentées par un tuple de 3 éléments :
- `case_depart` : Numéro de la case de départ (1-50)
- `case_arrivee` : Numéro de la case d'arrivée (1-50)
- `elimination` : 0 ou 1 indiquant s'il s'agit d'une élimination

### Architecture du Réseau Neuronal

Le réseau neuronal prend en entrée :
- L'état du plateau (50 cases jouables)
- L'action proposée (case départ, case arrivée, élimination)

Et retourne la valeur Q prédite pour cette paire état-action.

### Fonction de Récompense

La fonction de récompense est définie comme suit :
- +10 pour une victoire
- -10 pour une défaite
- +1 pour une capture (joueur 1)
- -1 pour une capture (joueur 0)
- +0.1 pour un déplacement simple (joueur 1)
- -0.1 pour un déplacement simple (joueur 0)
- 0 pour un match nul


## Dépendances

- Python 3.x
- TensorFlow 2.x
- NumPy
- Matplotlib
- Tkinter (pour l'interface graphique)


