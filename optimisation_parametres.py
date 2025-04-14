import numpy as np
import matplotlib.pyplot as plt
import os
from Plateau import Plateau
from IA_DQN import IA_DQN, train_self_play

def optimiser_hyperparametres():
    # Créer un dossier pour les résultats d'optimisation
    if not os.path.exists("optimisation_resultats"):
        os.makedirs("optimisation_resultats")
    
    # Paramètres à tester
    learning_rates = [0.001, 0.0005, 0.0001]
    gamma_values = [0.9, 0.95, 0.99]
    epsilon_decay_values = [0.99, 0.995, 0.999]    
    episodes = 3
    resultats = []
    
    # tester différentes combinaisons d'hyperparamètres
    for lr in learning_rates:
        for gamma in gamma_values:
            for epsilon_decay in epsilon_decay_values:
                print(f"\nTest avec learning_rate={lr}, gamma={gamma}, epsilon_decay={epsilon_decay}")

                agent = IA_DQN(learning_rate=lr, gamma=gamma, epsilon_decay=epsilon_decay)
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
                            
                            action = agent.act(state, actions_valides)# Choisir une action
                            plateau.deplacementIA(action)# Exécuter l'action
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
                            
                            # Vérifier s'il y a match nul (trop de coups sans capture)
                            if no_capture_count >= 50:
                                reward = 0
                                done = True
                            
                            # Stocker l'expérience dans la mémoire
                            agent.remember(state, action, reward, next_state, done,turn)
                            
                            # Mettre à jour l'état
                            state = next_state
                            total_reward += reward
                            
                            turn = 1 - turn

                        agent.replay(32)
                    
                    # Mettre à jour le modèle cible périodiquement
                    if episode % 10 == 0:
                        agent.update_target_model()
                    
                    # Enregistrer la récompense totale
                    rewards_history.append(total_reward)
                    
                    # Afficher les progrès
                    if episode % 10 == 0:
                        print(f"Épisode {episode+1}/{episodes}, Récompense: {total_reward}, Epsilon: {agent.epsilon:.4f}")
                
                # Calculer la moyenne des récompenses sur les derniers épisodes
                avg_reward = np.mean(rewards_history[-10:])
                
                # Stocker les résultats
                resultats.append({
                    'learning_rate': lr,
                    'gamma': gamma,
                    'epsilon_decay': epsilon_decay,
                    'avg_reward': avg_reward,
                    'rewards_history': rewards_history
                })
                
                # Tracer la courbe d'apprentissage pour cette combinaison
                plt.figure(figsize=(10, 6))
                plt.plot(rewards_history)
                plt.title(f"Courbe d'apprentissage (lr={lr}, gamma={gamma}, epsilon_decay={epsilon_decay})")
                plt.xlabel("Épisode")
                plt.ylabel("Récompense totale")
                plt.savefig(f"optimisation_resultats/learning_curve_lr{lr}_gamma{gamma}_eps{epsilon_decay}.png")
                plt.close()
    
    # Trouver la meilleure combinaison d'hyperparamètres
    resultats.sort(key=lambda x: x['avg_reward'], reverse=True)
    meilleur_resultat = resultats[0]
    
    print("\n=== Résultats de l'optimisation ===")
    print(f"Meilleure combinaison d'hyperparamètres:")
    print(f"Learning rate: {meilleur_resultat['learning_rate']}")
    print(f"Gamma: {meilleur_resultat['gamma']}")
    print(f"Epsilon decay: {meilleur_resultat['epsilon_decay']}")
    print(f"Récompense moyenne: {meilleur_resultat['avg_reward']}")
    
    # Entraîner un modèle final avec les meilleurs hyperparamètres
    print("\nEntraînement du modèle final avec les meilleurs hyperparamètres...")
    final_agent = IA_DQN(
        learning_rate=meilleur_resultat['learning_rate'],
        gamma=meilleur_resultat['gamma'],
        epsilon_decay=meilleur_resultat['epsilon_decay']
    )
    
    # Entraîner l'agent sur plus d'épisodes
    train_self_play(
        episodes=10,
        batch_size=32,
        target_update=10,
        save_interval=50,
        save_path="modele_optimise"
    )
    
    print("\nOptimisation terminée. Le modèle final est sauvegardé dans le dossier 'modele_optimise'.")
    
    return meilleur_resultat




meilleurs_params = optimiser_hyperparametres()


