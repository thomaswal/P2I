import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
from Plateau import Plateau

# Définition du réseau de neurones pour approximer la fonction Q
class DQN(nn.Module):
    def __init__(self, input_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.fc2 = nn.Linear(128, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.fc3 = nn.Linear(128, 1)  # Sortie unique pour la valeur Q

    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = torch.relu(self.bn2(self.fc2(x)))
        return self.fc3(x)

class IA_DQN:
    def __init__(self, plateau=Plateau(), alpha=0.001, gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur de réduction
        self.epsilon = epsilon  # Taux d'exploration
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.plateau = plateau
        self.r_elimination = 1
        self.r_victoire = 15
        self.r_defaite = -15
        self.r_dame = 3

        # Initialisation du réseau de neurones et de l'optimiseur
        self.model = DQN(input_dim=53)  # 50 cases + 3 infos de coup
        self.target_model = DQN(input_dim=53)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()
        self.optimizer = optim.Adam(self.model.parameters(), lr=alpha)
        self.loss_fn = nn.MSELoss()

        # Mémoire d'expérience pour l'apprentissage par renforcement
        self.memory = deque(maxlen=10000)

    def liste_plateau(self):
        res = []
        for i in range(1, 51):
            pion = self.plateau.plateau[i]
            if pion is None:
                res.append(0)
            else:
                joueur, est_dame = pion
                valeur = 1 if joueur == 1 else -1
                if est_dame:
                    valeur *= 2
                res.append(valeur)
        return res  # Retourne une liste de 50 nombres

    def coup_possible(self, tour):
        coup_possible = []
        for i in range(1, 51):
            pion = self.plateau.plateau[i]
            if pion is not None:
                joueur, est_dame = pion
                if joueur == tour:
                    if est_dame:
                        deplacement, elimination = self.plateau.deplacementDamesPossible(i)
                    else:
                        deplacement = self.plateau.deplacementsPossible(i)
                        elimination = self.plateau.eliminationsPossibles(i)

                    if elimination:
                        for j in elimination:
                            coup_possible.append((i, j, 1))
                    if deplacement:
                        for j in deplacement:
                            coup_possible.append((i, j, 0))
        return coup_possible

    def choisir_action(self, state, coup_possible):
        if coup_possible == []:
            return None  # Aucun coup possible

        if random.random() < self.epsilon:
            return random.choice(coup_possible)  # Exploration

        best_move = None
        best_q_value = float('-inf')
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)  # Ajouter une dimension de batch

        for move in coup_possible:
            action_tensor = torch.tensor(move, dtype=torch.float32).unsqueeze(0)  # Ajouter une dimension de batch
            input_tensor = torch.cat((state_tensor, action_tensor), dim=1)
            q_value = self.model(input_tensor)
            if q_value > best_q_value:
                best_q_value = q_value
                best_move = move

        return best_move


    def store_experience(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))

    def train(self):
        if len(self.memory) < 64:
            return  # Attendre d'avoir assez de données

        batch = random.sample(self.memory, 64)

        # Créer des listes pour stocker les états, actions, récompenses et nouveaux états
        states = []
        actions = []
        rewards = []
        next_states = []

        for state, action, reward, next_state in batch:
            states.append(state)
            actions.append(action)
            rewards.append(reward)
            next_states.append(next_state)

        # Convertir les listes en tenseurs
        states_tensor = torch.tensor(states, dtype=torch.float32)
        actions_tensor = torch.tensor(actions, dtype=torch.float32)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32)
        next_states_tensor = torch.tensor(next_states, dtype=torch.float32)

        # Concaténer les états et actions
        input_tensor = torch.cat((states_tensor, actions_tensor), dim=1)
        next_input_tensor = torch.cat((next_states_tensor, actions_tensor), dim=1)

        # Prédire les valeurs Q
        q_values = self.model(input_tensor)
        next_q_values = self.target_model(next_input_tensor)

        # Calculer les cibles Q
        targets = rewards_tensor + self.gamma * next_q_values

        # Calculer la perte
        loss = self.loss_fn(q_values, targets)

        # Mettre à jour les poids du réseau
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Mettre à jour le réseau cible
        self.update_target_model()

        # Mettre à jour le taux d'exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())


# Exemple d'utilisation
plateau = Plateau()
ia = IA_DQN(plateau=plateau)

# Boucle d'entraînement
for episode in range(5):
    state = ia.liste_plateau()
    done = False
    tour = 1  # Joueur 1 commence

    while not done:
        coup_possible = ia.coup_possible(tour)
        action = ia.choisir_action(state, coup_possible)
        if action is None:
            print(f"aucun coup possible pour le joueur {tour}")
            break

        ia.plateau.deplacementIA(action)
        next_state = ia.liste_plateau()

        reward = 0
        if ia.plateau.verifierVictoire(tour):
            reward = ia.r_victoire
            done = True
        if ia.plateau.verifierVictoire(1 if tour == 1 else 0):
            reward = ia.r_defaite
            done = True
        if action[2] == 1:
            reward = ia.r_elimination
        ia.store_experience(state, action, reward, next_state)
        state = next_state
        ia.train()

        # Changer de tour
        tour = 0 if tour == 1 else 1

    # Réinitialiser le plateau pour une nouvelle partie
    ia.plateau.reset()
    print(f"partie {episode + 1} terminé.")
