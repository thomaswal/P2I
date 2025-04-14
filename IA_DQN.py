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
        # Entrée pour l'état du plateau (50 cases jouables)
        plateau_input = keras.Input(shape=(50,), name="plateau_input")
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
        if not actions_valides:
            return None  # Aucune action valide
        
        if np.random.rand() <= self.epsilon:
            # Exploration: choisir une action aléatoire parmi les actions valides
            return random.choice(actions_valides)
        
        # Exploitation: choisir l'action avec la plus grande valeur Q
        q_values = []
        
        state_array = self._preprocess_state(state)
        
        for action in actions_valides:
            action_array = np.array(action).reshape(1, 3)
            q_value = self.model.predict([state_array, action_array], verbose=0)[0][0]
            q_values.append((action, q_value))
        
        q_values.sort(key=lambda x: x[1], reverse=True)
        return q_values[0][0]
    
    def replay(self, batch_size):

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
        processed_state = np.zeros((1, 50))
        
        for i in range(1, 51):
            if state[i] is None:
                processed_state[0, i-1] = 0  
            else:
                joueur, est_dame = state[i]
                # Encodage: 1 pour pion joueur 1, 2 pour dame joueur 1, -1 pour pion joueur 0, -2 pour dame joueur 0
                value = 1 if joueur == 1 else -1
                if est_dame:
                    value *= 2
                processed_state[0, i-1] = value
                
        return processed_state
    
    def _get_actions_valides(self, state, joueur_actuel):
        # Créer un plateau temporaire pour calculer les actions valides
        plateau_temp = Plateau()
        plateau_temp.plateau = state.copy()
        
        actions_valides = []
 
        
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
        
        # Prioriser les éliminations 
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
  
    # Entraîne l'agent en le faisant jouer contre lui-même
    

    # Créer le dossier 
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    

    agent = IA_DQN()
    
    rewards_history = []
    
    for episode in range(episodes):
        plateau = Plateau()
        state = plateau.getPlateau()
        total_reward = 0
        done = False
        turn = 1  
        no_capture_count = 0
        
        while not done:
            actions_valides = agent._get_actions_valides(state,turn)
            
            if not actions_valides:
                reward = -10 if turn == 1 else 10
                done = True
            else:
                action = agent.act(state, actions_valides)
                
                plateau.deplacementIA(action)
                
                next_state = plateau.getPlateau()
                
                if plateau.verifierVictoire(turn):
                    reward = 10 if turn == 1 else -10
                    done = True
                else:
                    # Récompense basée sur la capture
                    if action[2] == 1:  
                        reward = 1 if turn == 1 else -1
                        no_capture_count = 0
                    else:
                        reward = 0.1 if turn == 1 else -0.1
                        no_capture_count += 1
                
                if no_capture_count >= 50:
                    reward = 0
                    done = True
                
                # stocker l'expérience 
                agent.remember(state, action, reward, next_state, done,joueur_actuel=turn)
                state = next_state
                total_reward += reward
                
                turn = 1 - turn
            
            # entraîner l'agent
            agent.replay(batch_size)
        
        if episode % target_update == 0:
            agent.update_target_model()
        
        # sauvegarder le modèle périodiquement
        if episode % save_interval == 0:
            agent.save(f"{save_path}/model_episode_{episode}.h5")
        
        # enregistrer la récompense totale
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



