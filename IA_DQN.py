import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers # type: ignore
import random
from collections import deque
import matplotlib.pyplot as plt
import os
from Plateau import Plateau

class IA_DQN:
    def __init__(self, learning_rate=0.001, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, memory_size=10000):
        """
        Initialisation du modèle Deep Q-Learning pour le jeu de dames
        
        Args:
            learning_rate: Taux d'apprentissage pour l'optimiseur
            gamma: Facteur de réduction pour les récompenses futures
            epsilon: Paramètre d'exploration (probabilité de choisir une action aléatoire)
            epsilon_min: Valeur minimale d'epsilon
            epsilon_decay: Facteur de décroissance d'epsilon après chaque action
            memory_size: Taille de la mémoire de replay
        """
        self.learning_rate = learning_rate
        self.gamma = gamma  # facteur de réduction pour les récompenses futures
        self.epsilon = epsilon  # paramètre d'exploration
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.memory = deque(maxlen=memory_size)
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        
    def _build_model(self):
        """
        Construction du réseau de neurones pour le Deep Q-Learning
        
        Le réseau prend en entrée:
        - L'état du plateau (50 cases jouables)
        - L'action proposée (case départ, case arrivée, élimination)
        
        Et retourne la valeur Q prédite pour cette paire état-action
        """
        # Entrée pour l'état du plateau (50 cases jouables)
        plateau_input = keras.Input(shape=(50,), name="plateau_input")
        
        # Entrée pour l'action (case départ, case arrivée, élimination)
        action_input = keras.Input(shape=(3,), name="action_input")
        
        # Traitement de l'état du plateau
        x1 = layers.Dense(128, activation="relu")(plateau_input)
        x1 = layers.Dense(64, activation="relu")(x1)
        
        # Traitement de l'action
        x2 = layers.Dense(32, activation="relu")(action_input)
        
        # Concaténation des deux branches
        combined = layers.Concatenate()([x1, x2])
        
        # Couches communes
        x = layers.Dense(64, activation="relu")(combined)
        x = layers.Dense(32, activation="relu")(x)
        
        # Sortie: valeur Q prédite pour la paire état-action
        output = layers.Dense(1, activation="linear")(x)
        
        model = keras.Model(inputs=[plateau_input, action_input], outputs=output)
        model.compile(loss=keras.losses.MeanSquaredError(), optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate))
        
        return model
    
    def update_target_model(self):
        """Met à jour le modèle cible avec les poids du modèle principal"""
        self.target_model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done,joueur_actuel):
        """Stocke l'expérience dans la mémoire de replay"""
        self.memory.append((state, action, reward, next_state, done,joueur_actuel))
    
    def act(self, state, actions_valides):
        """
        Choisit une action selon la politique epsilon-greedy
        
        Args:
            state: État actuel du plateau (liste de 50 éléments)
            actions_valides: Liste des actions valides au format (case_depart, case_arrivee, elimination)
            
        Returns:
            L'action choisie au format (case_depart, case_arrivee, elimination)
        """
        if not actions_valides:
            return None  # Aucune action valide
        
        if np.random.rand() <= self.epsilon:
            # Exploration: choisir une action aléatoire parmi les actions valides
            return random.choice(actions_valides)
        
        # Exploitation: choisir l'action avec la plus grande valeur Q
        q_values = []
        
        # Convertir l'état en format approprié pour le réseau
        state_array = self._preprocess_state(state)
        
        for action in actions_valides:
            action_array = np.array(action).reshape(1, 3)
            q_value = self.model.predict([state_array, action_array], verbose=0)[0][0]
            q_values.append((action, q_value))
        
        # Trier par valeur Q décroissante et prendre la meilleure action
        q_values.sort(key=lambda x: x[1], reverse=True)
        return q_values[0][0]
    
    def replay(self, batch_size):
        """
        Entraîne le modèle en utilisant l'expérience replay
        
        Args:
            batch_size: Taille du lot d'expériences à utiliser pour l'entraînement
        """
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        
        states_plateau = []
        states_action = []
        targets = []
        
        for state, action, reward, next_state, done,joueur_actuel in minibatch:
            state_array = self._preprocess_state(state)
            action_array = np.array(action).reshape(1, 3)
            
            target = reward
            if not done:
                # Calculer les valeurs Q pour toutes les actions possibles dans l'état suivant
                next_state_array = self._preprocess_state(next_state)
                
                # Obtenir les actions valides pour l'état suivant
                next_actions_valides = self._get_actions_valides(next_state,joueur_actuel)
                
                if next_actions_valides:
                    max_q = float('-inf')
                    for next_action in next_actions_valides:
                        next_action_array = np.array(next_action).reshape(1, 3)
                        q = self.target_model.predict([next_state_array, next_action_array], verbose=0)[0][0]
                        max_q = max(max_q, q)
                    
                    target = reward + self.gamma * max_q
            
            states_plateau.append(state_array[0])
            states_action.append(action_array[0])
            targets.append(target)
        
        # Entraîner le modèle sur le lot
        self.model.fit(
            [np.array(states_plateau), np.array(states_action)],
            np.array(targets),
            epochs=1,
            verbose=0
        )
        
        # Réduire epsilon pour diminuer l'exploration au fil du temps
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def _preprocess_state(self, state):
        """
        Prétraite l'état du plateau pour le réseau neuronal
        
        Args:
            state: Liste représentant le plateau (51 éléments, index 0 non utilisé)
            
        Returns:
            Un tableau numpy de forme (1, 50) représentant les cases jouables
        """
        # Ignorer l'index 0 et convertir les tuples en valeurs numériques
        processed_state = np.zeros((1, 50))
        
        for i in range(1, 51):
            if state[i] is None:
                processed_state[0, i-1] = 0  # Case vide
            else:
                joueur, est_dame = state[i]
                # Encodage: 1 pour pion joueur 1, 2 pour dame joueur 1, -1 pour pion joueur 0, -2 pour dame joueur 0
                value = 1 if joueur == 1 else -1
                if est_dame:
                    value *= 2
                processed_state[0, i-1] = value
                
        return processed_state
    
    def _get_actions_valides(self, state, joueur_actuel):
        """
        Obtient toutes les actions valides pour un état donné
        
        Args:
            state: État du plateau
            
        Returns:
            Liste des actions valides au format (case_depart, case_arrivee, elimination)
        """
        # Créer un plateau temporaire pour calculer les actions valides
        plateau_temp = Plateau()
        plateau_temp.plateau = state.copy()
        
        actions_valides = []
 
        
        # Parcourir toutes les cases du plateau
        for i in range(1, 51):
            pion = plateau_temp.plateau[i]
            if pion is not None:
                joueur, est_dame = pion
                if joueur == joueur_actuel:
                    if est_dame:
                        deplacement, elimination = plateau_temp.deplacementDamesPossible(i)
                    else:
                        deplacement = plateau_temp.deplacementsPossible(i)
                        elimination = plateau_temp.eliminationsPossibles(i)

                    if elimination:
                        for j in elimination:
                            actions_valides.append((i, j, 1))
                    if deplacement:
                        for j in deplacement:
                            actions_valides.append((i, j, 0))
        
        # Prioriser les éliminations (règle du jeu de dames)
        eliminations_actions = [action for action in actions_valides if action[2] == 1]
        if eliminations_actions:
            return eliminations_actions
        
        return actions_valides
    
    
    def save(self, filepath):
        """Sauvegarde le modèle"""
        self.model.save(filepath)
    
    def load(self, filepath):
        """Charge un modèle préentraîné"""
        self.model = keras.models.load_model(filepath)
        self.update_target_model()


def train_self_play(episodes=1000, batch_size=32, target_update=10, save_interval=100, save_path="dames_dqn_model"):
    """
    Entraîne l'agent en le faisant jouer contre lui-même
    
    Args:
        episodes: Nombre d'épisodes d'entraînement
        batch_size: Taille du lot pour l'apprentissage
        target_update: Fréquence de mise à jour du modèle cible
        save_interval: Fréquence de sauvegarde du modèle
        save_path: Chemin de sauvegarde du modèle
    """
    # Créer le dossier de sauvegarde s'il n'existe pas
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # Initialiser l'agent
    agent = IA_DQN()
    
    # Historique des récompenses pour suivre les progrès
    rewards_history = []
    
    for episode in range(episodes):
        # Initialiser le plateau
        plateau = Plateau()
        state = plateau.getPlateau()
        total_reward = 0
        done = False
        turn = 1  # Commencer avec le joueur 1
        
        # Compteur de coups sans capture
        no_capture_count = 0
        
        while not done:
            # Obtenir les actions valides pour le joueur actuel
            actions_valides = agent._get_actions_valides(state,turn)
            
            if not actions_valides:
                # Si aucune action valide, le joueur actuel a perdu
                reward = -10 if turn == 1 else 10
                done = True
            else:
                # Choisir une action
                action = agent.act(state, actions_valides)
                
                # Exécuter l'action
                plateau.deplacementIA(action)
                
                # Obtenir le nouvel état
                next_state = plateau.getPlateau()
                
                # Vérifier si le jeu est terminé
                if plateau.verifierVictoire(turn):
                    reward = 10 if turn == 1 else -10
                    done = True
                else:
                    # Récompense basée sur la capture
                    if action[2] == 1:  # Si c'est une élimination
                        reward = 1 if turn == 1 else -1
                        no_capture_count = 0
                    else:
                        reward = 0.1 if turn == 1 else -0.1
                        no_capture_count += 1
                
                # Vérifier s'il y a match nul (trop de coups sans capture)
                if no_capture_count >= 50:
                    reward = 0
                    done = True
                
                # Stocker l'expérience dans la mémoire
                agent.remember(state, action, reward, next_state, done,joueur_actuel=turn)
                
                
                # Mettre à jour l'état
                state = next_state
                total_reward += reward
                
                # Changer de joueur
                turn = 1 - turn
            
            # Entraîner l'agent
            agent.replay(batch_size)
        
        # Mettre à jour le modèle cible périodiquement
        if episode % target_update == 0:
            agent.update_target_model()
        
        # Sauvegarder le modèle périodiquement
        if episode % save_interval == 0:
            agent.save(f"{save_path}/model_episode_{episode}.h5")
        
        # Enregistrer la récompense totale
        rewards_history.append(total_reward)
        
        # Afficher les progrès
        print(f"Épisode {episode+1}/{episodes}, Récompense: {total_reward}, Epsilon: {agent.epsilon:.4f}")
    
    # Sauvegarder le modèle final
    agent.save(f"{save_path}/model_final.h5")
    
    # Tracer la courbe d'apprentissage
    plt.figure(figsize=(10, 6))
    plt.plot(rewards_history)
    plt.title("Courbe d'apprentissage")
    plt.xlabel("Épisode")
    plt.ylabel("Récompense totale")
    plt.savefig(f"{save_path}/learning_curve.png")
    
    return agent


def play_game(agent, human_player=True):
    """
    Joue une partie contre l'agent ou fait jouer l'agent contre lui-même
    
    Args:
        agent: Agent IA_DQN entraîné
        human_player: Si True, l'utilisateur joue contre l'agent, sinon l'agent joue contre lui-même
    """
    from GraphiquePlateau import GraphiquePlateau
    
    # Initialiser le plateau graphique
    graphique_plateau = GraphiquePlateau()
    plateau = graphique_plateau.get_plateau()
    
    # Afficher le plateau
    if human_player:
        graphique_plateau.afficher_plateau()
    else:
        # Mode IA vs IA (pour démonstration)
        state = plateau.getPlateau()
        turn = 1  # Commencer avec le joueur 1
        
        while True:
            # Obtenir les actions valides pour le joueur actuel
            actions_valides = agent._get_actions_valides(state)
            
            if not actions_valides or plateau.verifierVictoire(turn):
                break
            
            # Choisir une action
            action = agent.act(state, actions_valides)
            
            # Exécuter l'action
            plateau.deplacementIA(action)
            
            # Mettre à jour l'affichage
            graphique_plateau.actualiser_affichage()
            
            # Obtenir le nouvel état
            state = plateau.getPlateau()

