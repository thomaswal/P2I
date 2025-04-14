from IA_DQN import train_self_play

# entraîne l'agent sur 1000 épisodes
agent = train_self_play(episodes=10)

# sauvegarder le modèle 
agent.save("mon_modele.h5")

