from IA_DQN import train_self_play

# Entraîner l'agent sur 1000 épisodes
agent = train_self_play(episodes=10)

# Sauvegarder le modèle entraîné
agent.save("mon_modele.h5")

