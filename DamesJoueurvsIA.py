from tkinter import *
import time
import os
import numpy as np
from Plateau import Plateau
from IA_DQN import IA_DQN

class DamesJoueurvsIA:
    def __init__(self, agent_ia=None, joueur_humain_couleur=1, apprentissage_continu=True):

        self.plateau = Plateau()
        self.listeRect = []
        self.deplacementsPossibles = []
        self.eliminationsPossibles = []
        self.multiEliminations = False
        self.canvas = None
        self.listePions = []
        self.taille_case = 50
        self.case_selectionnee = None 
        self.redCountLabel = None
        self.blueCountLabel = None
        self.noCaptureOrMoveCount = 0
        self.turnsSinceLastCaptureOrMove = 0
        
        self.joueur_humain_couleur = joueur_humain_couleur
        self.tour_joueur_humain = (joueur_humain_couleur == 1)  
        self.turn = 1  
        self.turnLabel = None
        self.statusLabel = None
        self.learningLabel = None
        
        
        self.apprentissage_continu = apprentissage_continu
        self.memoire_partie = []  
        
        if agent_ia is None:
            self.agent = IA_DQN(epsilon=0.1)  
        else:
            self.agent = agent_ia
        
        self.fenetre = None
        self.partie_en_cours = True
        
        self.previous_state = None
        self.previous_action = None
        
    def afficher_plateau(self):
        self.fenetre = Tk()
        self.fenetre.title("Jeu de Dames - Joueur vs IA avec Apprentissage Continu")
        self.fenetre.geometry("500x1000")
        
        info_frame = Frame(self.fenetre)
        info_frame.pack(pady=10)
        
        self.turnLabel = Label(info_frame, text="Tour du joueur rouge", font=("Arial", 20))
        self.turnLabel.pack()
        
        self.statusLabel = Label(info_frame, text="", font=("Arial", 14), fg="blue")
        self.statusLabel.pack()
        
        self.learningLabel = Label(info_frame, text="Apprentissage continu: " + 
                                  ("Activé" if self.apprentissage_continu else "Désactivé"), 
                                  font=("Arial", 12), fg="green" if self.apprentissage_continu else "red")
        self.learningLabel.pack()
        
        self.redCountLabel = Label(info_frame, text="", font=("Arial", 14))
        self.redCountLabel.pack()
        self.blueCountLabel = Label(info_frame, text="", font=("Arial", 14))
        self.blueCountLabel.pack()
        self.update_piece_count()
        
        self.canvas = Canvas(self.fenetre, width=500, height=500)
        self.canvas.pack(pady=10)
        
        for i in range(10):
            for j in range(10):
                couleur = "lightgrey" if (i + j) % 2 == 0 else "white"
                x1, y1 = i * self.taille_case, j * self.taille_case
                x2, y2 = x1 + self.taille_case, y1 + self.taille_case
                r = self.canvas.create_rectangle(x1, y1, x2, y2, fill=couleur, outline="black")
                self.listeRect.append(r)
        
        self.actualiser_affichage()
        
        control_frame = Frame(self.fenetre)
        control_frame.pack(pady=5)
        
        Button(control_frame, text="Activer apprentissage", 
               command=self.activer_apprentissage).pack(side=LEFT, padx=5)
        Button(control_frame, text="Désactiver apprentissage", 
               command=self.desactiver_apprentissage).pack(side=LEFT, padx=5)
        Button(control_frame, text="Nouvelle partie", 
               command=self.nouvelle_partie).pack(side=LEFT, padx=5)
        Button(control_frame, text="Sauvegarder IA", 
               command=self.sauvegarder_ia).pack(side=LEFT, padx=5)
        
        self.canvas.bind("<Button-1>", self.gestion_clic)
        
        self.previous_state = self.plateau.getPlateau().copy()
        
        if not self.tour_joueur_humain:
            self.fenetre.after(1000, self.tour_ia)
        
        self.fenetre.mainloop()
    
    def activer_apprentissage(self):
        """Active l'apprentissage continu"""
        self.apprentissage_continu = True
        self.learningLabel.config(text="Apprentissage continu: Activé", fg="green")
    
    def desactiver_apprentissage(self):
        """Désactive l'apprentissage continu"""
        self.apprentissage_continu = False
        self.learningLabel.config(text="Apprentissage continu: Désactivé", fg="red")
    
    def sauvegarder_ia(self):
        """Sauvegarde le modèle de l'IA"""
        if not os.path.exists("dames_dqn_model"):
            os.makedirs("dames_dqn_model")
        
        # sauvegarder le modèle
        save_path = "dames_dqn_model/model_apprentissage_continu.h5"
        self.agent.save(save_path)
        
        top = Toplevel(self.fenetre)
        top.title("Sauvegarde")
        msg = Message(top, text=f"Modèle sauvegardé avec succès dans {save_path}", 
                     font=("Arial", 14), width=300)
        msg.pack(pady=20)
        Button(top, text="OK", command=top.destroy).pack(pady=10)
    
    def gestion_clic(self, event):
        if not self.tour_joueur_humain or not self.partie_en_cours:
            return
        
        # Calculer la case cliquée
        x = event.x // 50 + 1 
        y = event.y // 50 + 1
        num_case = (y-1)*5 + (1-(x%2))*(x//2) + (x%2)*((x//2)+1)
        
        if self.case_selectionnee is None:  # Premier clic (sélection d'un pion)
            pion = self.plateau.plateau[num_case]
            if pion is not None:
                joueur, est_dame = pion
                if joueur == self.joueur_humain_couleur:  # Vérifier que c'est un pion du joueur humain
                    if est_dame:
                        self.deplacementsPossibles = self.plateau.deplacementDamesPossible(num_case)[0]
                        self.eliminationsPossibles = self.plateau.deplacementDamesPossible(num_case)[1]
                        if self.deplacementsPossibles == [] and self.eliminationsPossibles == []:
                            self.case_selectionnee = None
                        else:
                            self.case_selectionnee = num_case 
                            
                            # Colorer les cases possibles
                            for case_possible in self.deplacementsPossibles:
                                self.colorierCaseVert(case_possible)
                            for case_possible in self.eliminationsPossibles:
                                self.colorierCaseOrange(case_possible)
                    else:
                        self.deplacementsPossibles = self.plateau.deplacementsPossible(num_case)
                        self.eliminationsPossibles = self.plateau.eliminationsPossibles(num_case)
                        if self.deplacementsPossibles == [] and self.eliminationsPossibles == []:
                            self.case_selectionnee = None
                        else:
                            self.case_selectionnee = num_case 
                            
                            # Colorer les cases possibles
                            for case_possible in self.deplacementsPossibles:
                                self.colorierCaseVert(case_possible)
                            for case_possible in self.eliminationsPossibles:
                                self.colorierCaseOrange(case_possible)
        
        else:  # Deuxième clic (déplacement ou élimination)
            pion = self.plateau.plateau[self.case_selectionnee]
            joueur, est_dame = pion
            
            if num_case in self.deplacementsPossibles:  # Déplacement simple
                # Effacer les colorations
                for case_possible in self.deplacementsPossibles:
                    self.decolorier_case(case_possible) 
                for case_possible in self.eliminationsPossibles:
                    self.decolorier_case(case_possible)
                
                action_joueur = (self.case_selectionnee, num_case, 0)  # 0 pour déplacement
                
                self.plateau.deplacer(self.case_selectionnee, num_case)
                
                self.actualiser_affichage()
                
                self.turnsSinceLastCaptureOrMove = 0
                self.noCaptureOrMoveCount += 1
                
                self.fin_tour_joueur(action_joueur)
                
            elif num_case in self.eliminationsPossibles:  # Élimination
                # Effacer les colorations
                for case_possible in self.deplacementsPossibles:
                    self.decolorier_case(case_possible) 
                for case_possible in self.eliminationsPossibles:
                    self.decolorier_case(case_possible)
                
                action_joueur = (self.case_selectionnee, num_case, 1)  # 1 pour élimination
                
                self.plateau.eliminer(self.case_selectionnee, num_case)
                self.actualiser_affichage()
                
                # Vérifier s'il y a d'autres éliminations possibles
                if est_dame:
                    self.eliminationsPossibles = self.plateau.deplacementDamesPossible(num_case)[1]
                else:
                    self.eliminationsPossibles = self.plateau.eliminationsPossibles(num_case)
                
                if self.eliminationsPossibles != []:  # Si d'autres éliminations sont possibles
                    self.multiEliminations = True
                    self.case_selectionnee = num_case
                    self.deplacementsPossibles = []
                    for i in self.eliminationsPossibles:
                        self.colorierCaseOrange(i)
                else:
                    # Mettre à jour les compteurs
                    self.turnsSinceLastCaptureOrMove = 0
                    self.noCaptureOrMoveCount = 0
                    
                    # Passer au tour de l'IA
                    self.fin_tour_joueur(action_joueur)
                
                # Mettre à jour le compteur de pions
                self.update_piece_count()
                
            elif self.multiEliminations:  # Si le joueur aurait pu faire une autre élimination
                self.multiEliminations = False
                self.turnsSinceLastCaptureOrMove += 1
                
                # Passer au tour de l'IA sans action spécifique
                self.fin_tour_joueur(None)
                
            else:  # Clic sur une case non valide
                # Effacer les colorations
                for case_possible in self.deplacementsPossibles:
                    self.decolorier_case(case_possible) 
                for case_possible in self.eliminationsPossibles:
                    self.decolorier_case(case_possible)
                
                # Réinitialiser la sélection
                self.case_selectionnee = None
                self.deplacementsPossibles = []
                self.eliminationsPossibles = []
                self.turnsSinceLastCaptureOrMove += 1
    
    def fin_tour_joueur(self, action_joueur):
        self.case_selectionnee = None
        self.deplacementsPossibles = []
        self.eliminationsPossibles = []
        self.multiEliminations = False
        
        current_state = self.plateau.getPlateau().copy()
        
        if self.apprentissage_continu and action_joueur and self.previous_state:
            # Calculer la récompense pour l'IA (négative car c'est le coup du joueur)
            reward = -0.1
            if action_joueur[2] == 1:  
                reward = -1  
            
            if self.plateau.verifierVictoire(self.joueur_humain_couleur):
                reward = -10  # Forte pénalité si le joueur gagne
                
            self.agent.remember(self.previous_state, action_joueur, reward, current_state, False, self.turn)
            
            if len(self.agent.memory) >= 32:
                self.agent.replay(32)
                self.statusLabel.config(text="L'IA apprend de votre coup...")
        
        self.previous_state = current_state
        
        self.switch_turn()
        
        if self.partie_en_cours:
            self.statusLabel.config(text="L'IA réfléchit...")
            self.fenetre.after(1000, self.tour_ia)
    
    def tour_ia(self):
        """Fait jouer l'IA"""
        if not self.partie_en_cours:
            return
        
        state = self.plateau.getPlateau().copy()
        
        actions_valides = self.agent._get_actions_valides(state,self.turn)
        
        if not actions_valides:
            self.partie_en_cours = False
            self.show_message(f"Victoire du joueur {'rouge' if self.joueur_humain_couleur == 1 else 'bleu'}!")
            return
        
        action = self.agent.act(state, actions_valides)
        
        case_depart, case_arrivee, elimination = action
        

        
        if elimination:
            self.colorierCaseOrange(case_arrivee)
        else:
            self.colorierCaseVert(case_arrivee)
        self.fenetre.update()
        time.sleep(0.5)
        
        self.plateau.deplacementIA(action)
        
        self.decolorier_case(case_arrivee)  # Effacer la case de départ
        self.actualiser_affichage()
        
        next_state = self.plateau.getPlateau().copy()
        
        reward = 0.1  # Récompense de base pour un déplacement
        if elimination:
            reward = 1  # Récompense plus importante pour une capture
            self.turnsSinceLastCaptureOrMove = 0
            self.noCaptureOrMoveCount = 0
        else:
            self.turnsSinceLastCaptureOrMove = 0
            self.noCaptureOrMoveCount += 1
        
        done = False
        if self.plateau.verifierVictoire(1 - self.joueur_humain_couleur):
            reward = 10  # Forte récompense si l'IA gagne
            done = True
            self.partie_en_cours = False
            self.show_message(f"Victoire de l'IA ({('bleu' if self.joueur_humain_couleur == 1 else 'rouge')})!")
        
        if self.apprentissage_continu and self.previous_state:
            # Stocker l'expérience dans la mémoire de l'agent
            self.agent.remember(self.previous_state, action, reward, next_state, done, self.turn)
            
            # Entraîner l'agent avec un petit lot d'expériences
            if len(self.agent.memory) >= 32:
                self.agent.replay(32)
        
        # Mettre à jour l'état précédent
        self.previous_state = next_state
        
        self.update_piece_count()
        
        if self.partie_en_cours:
            # Passer au tour du joueur
            self.switch_turn()
            self.statusLabel.config(text="À votre tour!")
    
    def actualiser_affichage(self):
        self.canvas.delete("pion")  # Supprimer tous les pions
        
        for i in range(1, 51):
            pion = self.plateau.plateau[i]
            if pion is not None:
                joueur, est_dame = pion
                row = (i - 1) // 5
                col = ((i - 1) % 5) * 2 + (row % 2)

                x1 = col * self.taille_case + 10
                y1 = row * self.taille_case + 10
                x2 = x1 + self.taille_case - 20
                y2 = y1 + self.taille_case - 20

                couleur = "red" if joueur == 1 else "blue"
                self.canvas.create_oval(x1, y1, x2, y2, fill=couleur, outline="black", tags="pion")
                
                if est_dame:
                    self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="D", font=("Arial", 16, "bold"), fill="gold", tags="pion")
    
    def colorierCaseVert(self, num_case):
        if num_case < 1 or num_case > 50:
            return
        
        ligne = (num_case - 1) // 5
        colonne = ((num_case - 1) % 5) * 2 + (ligne % 2)

        x1, y1 = colonne * self.taille_case, ligne * self.taille_case
        x2, y2 = x1 + self.taille_case, y1 + self.taille_case

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
    
    def colorierCaseOrange(self, num_case):
        if num_case < 1 or num_case > 50:
            return
        
        ligne = (num_case - 1) // 5
        colonne = ((num_case - 1) % 5) * 2 + (ligne % 2)

        x1, y1 = colonne * self.taille_case, ligne * self.taille_case
        x2, y2 = x1 + self.taille_case, y1 + self.taille_case

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="orange", outline="black")
    
    def decolorier_case(self, num_case):
        if num_case < 1 or num_case > 50:
            return
        
        ligne = (num_case - 1) // 5
        colonne = ((num_case - 1) % 5) * 2 + (ligne % 2)

        x1, y1 = colonne * self.taille_case, ligne * self.taille_case
        x2, y2 = x1 + self.taille_case, y1 + self.taille_case

        couleur = "lightgrey" if (colonne + ligne) % 2 == 0 else "white"
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=couleur, outline="black")
    
    def switch_turn(self):
        if self.turn == 0:
            self.turn = 1
        else:
            self.turn = 0
        
        self.tour_joueur_humain = (self.turn == self.joueur_humain_couleur)
        self.update_turn_label()
    
    def update_turn_label(self):
        if self.turnLabel:
            if self.tour_joueur_humain:
                self.turnLabel.config(text=f"Tour du joueur {'rouge' if self.joueur_humain_couleur == 1 else 'bleu'}")
            else:
                self.turnLabel.config(text=f"Tour de l'IA {'bleu' if self.joueur_humain_couleur == 1 else 'rouge'}")
    
    def update_piece_count(self):
        red_count, blue_count = self.plateau.compteurPions()
        self.redCountLabel.config(text=f"Pions rouges: {red_count}")
        self.blueCountLabel.config(text=f"Pions bleus: {blue_count}")
        self.check_victory_or_draw(red_count, blue_count)
    
    def check_victory_or_draw(self, red_count, blue_count):
        if red_count == 0:
            self.partie_en_cours = False
            self.show_message("Victoire du joueur bleu!")
        elif blue_count == 0:
            self.partie_en_cours = False
            self.show_message("Victoire du joueur rouge!")
        elif self.noCaptureOrMoveCount >= 25:
            self.partie_en_cours = False
            self.show_message("Match nul: 25 coups sans déplacement ni prise.")
        elif self.turnsSinceLastCaptureOrMove >= 16:
            self.check_endgame_draw_conditions()
    
    def check_endgame_draw_conditions(self):
        red_pieces = [pion for pion in self.plateau.plateau if pion and pion[0] == 1]
        blue_pieces = [pion for pion in self.plateau.plateau if pion and pion[0] == 0]
        
        if self.is_endgame_draw(red_pieces, blue_pieces):
            self.partie_en_cours = False
            self.show_message("Match nul: conditions de fin de partie atteintes.")
    
    def is_endgame_draw(self, red_pieces, blue_pieces):
        red_dames = sum(1 for pion in red_pieces if pion[1])
        blue_dames = sum(1 for pion in blue_pieces if pion[1])
        red_pions = len(red_pieces) - red_dames
        blue_pions = len(blue_pieces) - blue_dames

        if (red_dames == 2 and blue_dames == 1) or (red_dames == 1 and blue_dames == 2):
            return True
        if (red_dames == 1 and red_pions <= 2 and blue_dames == 1 and blue_pions <= 2):
            return True
        if (red_dames == 1 and blue_dames == 1):
            return True
        return False
    
    def show_message(self, message):
        top = Toplevel(self.fenetre)
        top.title("Fin de partie")
        msg = Message(top, text=message, font=("Arial", 20))
        msg.pack(pady=20)
        
        # Boutons pour les actions possibles
        button_frame = Frame(top)
        button_frame.pack(pady=10)
        
        Button(button_frame, text="Nouvelle partie", command=lambda: self.nouvelle_partie(top)).pack(side=LEFT, padx=10)
        Button(button_frame, text="Sauvegarder IA", command=lambda: [self.sauvegarder_ia(), top.destroy()]).pack(side=LEFT, padx=10)
        Button(button_frame, text="Fermer", command=top.destroy).pack(side=LEFT, padx=10)
    
    def nouvelle_partie(self, popup=None):
        if popup:
            popup.destroy()
        
        # Réinitialiser le plateau
        self.plateau.reset()
        
        # Réinitialiser les variables
        self.case_selectionnee = None
        self.deplacementsPossibles = []
        self.eliminationsPossibles = []
        self.multiEliminations = False
        self.noCaptureOrMoveCount = 0
        self.turnsSinceLastCaptureOrMove = 0
        self.partie_en_cours = True
        
        # Réinitialiser le tour
        self.turn = 1  # Le joueur rouge commence toujours
        self.tour_joueur_humain = (self.joueur_humain_couleur == 1)
        
        # Mettre à jour l'affichage
        self.actualiser_affichage()
        self.update_turn_label()
        self.update_piece_count()
        
        # Stocker l'état initial
        self.previous_state = self.plateau.getPlateau().copy()
        
        # Si l'IA commence, faire jouer l'IA
        if not self.tour_joueur_humain:
            self.statusLabel.config(text="L'IA réfléchit...")
            self.fenetre.after(1000, self.tour_ia)
        else:
            self.statusLabel.config(text="À votre tour!")


def jouer_contre_ia(model_path=None, joueur_humain_couleur=1, apprentissage_continu=True):

    # Créer l'agent IA
    agent = IA_DQN(epsilon=0.1)  # Epsilon bas pour moins d'exploration en mode jeu
    
    # Charger un modèle préentraîné si spécifié
    if model_path and os.path.exists(model_path):
        try:
            agent.load(model_path)
            print(f"Modèle chargé depuis {model_path}")
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {e}")
    
    # Créer l'interface graphique
    jeu = DamesJoueurvsIA(agent, joueur_humain_couleur, apprentissage_continu)
    
    # Afficher le plateau et démarrer le jeu
    jeu.afficher_plateau()


if __name__ == "__main__":
    # Chercher un modèle préentraîné dans le dossier dames_dqn_model
    model_path = None
    if os.path.exists("dames_dqn_model"):
        models = [f for f in os.listdir("dames_dqn_model") if f.endswith(".h5")]
        if models:
            # Utiliser le modèle final s'il existe, sinon prendre le dernier modèle
            if "model_final.h5" in models:
                model_path = os.path.join("dames_dqn_model", "model_final.h5")
            elif "model_apprentissage_continu.h5" in models:
                model_path = os.path.join("dames_dqn_model", "model_apprentissage_continu.h5")
            else:
                models.sort()
                model_path = os.path.join("dames_dqn_model", models[-1])
    
    jouer_contre_ia(model_path, apprentissage_continu=True)
