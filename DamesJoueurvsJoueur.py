from tkinter import *
from Plateau import Plateau
from IA_DQN import IA_DQN
import time

class DamesJoueurvsJoueur:
    def __init__(self):
        self.plateau =Plateau()
        self.listeRect = []
        self.deplacementsPossibles = []
        self.eliminationsPossibles = []
        self.multiEliminations= False
        self.canvas = None
        self.listePions = []
        self.turn = self.plateau.turn
        self.turnLabel = None
        self.taille_case=50
        self.case_selectionnee = None 
        self.redCountLabel = None
        self.blueCountLabel = None
        self.noCaptureOrMoveCount = 0
        self.turnsSinceLastCaptureOrMove = 0
        

    def afficher_plateau(self):
        fenetre = Tk()
        fenetre.title("Jeu de Dames")
        fenetre.geometry("500x600")

        if self.turn==1:
            self.turnLabel = Label(fenetre, text="Tour du joueur rouge ", font=("Arial", 20))
            self.turnLabel.pack()
        else :
            self.turnLabel = Label(fenetre, text="Tour du joueur bleu", font=("Arial", 20))
            self.turnLabel.pack()

        self.redCountLabel = Label(fenetre, text="", font=("Arial", 14))
        self.redCountLabel.pack()
        self.blueCountLabel = Label(fenetre, text="", font=("Arial", 14))
        self.blueCountLabel.pack()
        self.update_piece_count()

        self.canvas = Canvas(fenetre, width=500, height=500)
        self.canvas.pack()

        for i in range(10):
            for j in range(10):
                couleur = "lightgrey" if (i + j) % 2 == 0 else "white"
                x1, y1 = i * self.taille_case, j * self.taille_case
                x2, y2 = x1 + self.taille_case, y1 + self.taille_case
                r = self.canvas.create_rectangle(x1, y1, x2, y2, fill=couleur, outline="black")
                self.listeRect.append(r)

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
                    self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="D", font=("Arial", 16, "bold"), fill="gold",tags="pion")


        self.canvas.bind("<Button-1>", self.gestion_clic)

       
        fenetre.mainloop()
    
    def gestion_clic(self, event):
        x = event.x // 50 +1 
        y = event.y // 50 +1

        num_case= (y-1)*5 + (1-(x%2))*(x//2) + (x%2)*((x//2)+1)

        if self.case_selectionnee is None:  # Premier clic
            pion = self.plateau.plateau[num_case]
            if pion is not None:
                joueur, est_dame = pion
                if joueur == self.turn: # test tour
                    if est_dame:
                        self.deplacementsPossibles = self.plateau.deplacementDamesPossible(num_case)[0]
                        self.eliminationsPossibles = self.plateau.deplacementDamesPossible(num_case)[1]
                        if self.deplacementsPossibles == [] and self.eliminationsPossibles==[]: #selection d'un pion que si il peut bouger
                            self.case_selectionnee = None
                        else:
                            self.case_selectionnee = num_case 

                        for case_possible in self.deplacementsPossibles:
                            self.colorierCaseVert(case_possible)  # colorer les cases où il peut aller en vert
                        for case_possible in self.eliminationsPossibles:
                            self.colorierCaseOrange(case_possible)  # colorer les cases où il peut manger en orange
                        print(f"Pion sélectionné : {num_case}, déplacements possibles : {self.deplacementsPossibles}, eliminations possibles : {self.eliminationsPossibles}.")

                    else:
                        self.deplacementsPossibles = self.plateau.deplacementsPossible(num_case)
                        self.eliminationsPossibles = self.plateau.eliminationsPossibles(num_case)
                        if self.deplacementsPossibles == [] and self.eliminationsPossibles==[]: #selection d'un pion que si il peut bouger
                            self.case_selectionnee = None
                        else:
                            self.case_selectionnee = num_case 

                        for case_possible in self.deplacementsPossibles:
                            self.colorierCaseVert(case_possible)  # colorer les cases où il peut aller en vert
                        for case_possible in self.eliminationsPossibles:
                            self.colorierCaseOrange(case_possible)  # colorer les cases où il peut manger en orange
                        print(f"Pion sélectionné : {num_case}, déplacements possibles : {self.deplacementsPossibles}, eliminations possibles : {self.eliminationsPossibles}.")

        else:  # Deuxième clic 
            pion = self.plateau.plateau[self.case_selectionnee]
            joueur, est_dame = pion
            if num_case in self.deplacementsPossibles:
                for case_possible in self.deplacementsPossibles:
                    self.decolorier_case(case_possible) 
                for case_possible in self.eliminationsPossibles:
                    self.decolorier_case(case_possible)  #efface les cases

                if est_dame:
                    self.plateau.deplacer(self.case_selectionnee,num_case) #deplacement sur la plateau
                    self.actualiser_affichage() 


                    print("deplacemetn fait")
                    print(f"Pion déplacé de {self.case_selectionnee} à {num_case}. Tour du joueur {'bleu' if self.turn == 1 else 'rouge'}.")
                    self.turnsSinceLastCaptureOrMove = 0
                    self.noCaptureOrMoveCount += 1
                    self.switch_turn()
                else:
                    self.plateau.deplacer(self.case_selectionnee,num_case) #deplacement sur la plateau
                    self.actualiser_affichage() 
                    print(f"Pion déplacé de {self.case_selectionnee} à {num_case}. Tour du joueur {'bleu' if self.turn == 1 else 'rouge'}.")
                    self.turnsSinceLastCaptureOrMove = 0
                    self.noCaptureOrMoveCount += 1
                    self.switch_turn()
                self.update_piece_count()
            elif num_case in self.eliminationsPossibles:
                for case_possible in self.deplacementsPossibles:
                    self.decolorier_case(case_possible) 
                for case_possible in self.eliminationsPossibles:
                    self.decolorier_case(case_possible)  #efface les cases

                if est_dame:
                    self.plateau.eliminer(self.case_selectionnee, num_case)
                    self.actualiser_affichage()
                    print(f"Pion éliminé en {num_case}.")
                    self.eliminationsPossibles = self.plateau.deplacementDamesPossible(num_case)[1]
                    if self.eliminationsPossibles != []: #si il peut encore manger
                        self.multiEliminations = True
                        self.case_selectionnee = num_case
                        self.deplacementsPossibles = []
                        for i in self.eliminationsPossibles:
                            self.colorierCaseOrange(i)
                    else:
                        self.turnsSinceLastCaptureOrMove = 0
                        self.noCaptureOrMoveCount = 0
                        self.switch_turn()
                    self.update_piece_count()
                else:
                    self.plateau.eliminer(self.case_selectionnee, num_case)
                    self.actualiser_affichage()
                    print(f"Pion éliminé en {num_case}.")
                    self.eliminationsPossibles = self.plateau.eliminationsPossibles(num_case)
                    if self.eliminationsPossibles != []: #si il peut encore manger
                        self.multiEliminations = True
                        self.case_selectionnee = num_case
                        self.deplacementsPossibles = []
                        for i in self.eliminationsPossibles:
                            self.colorierCaseOrange(i)
                    else:
                        self.turnsSinceLastCaptureOrMove = 0
                        self.noCaptureOrMoveCount = 0
                        self.switch_turn()
                    self.update_piece_count()
            elif self.multiEliminations:
                print("Vous auriez pu mangez un autre pion")
                self.multiEliminations=False
                self.turnsSinceLastCaptureOrMove += 1
                self.switch_turn()
            else:
                for case_possible in self.deplacementsPossibles:
                    self.decolorier_case(case_possible) 
                for case_possible in self.eliminationsPossibles:
                    self.decolorier_case(case_possible)  #efface les cases
                self.case_selectionnee = None
                self.deplacementsPossibles = []
                self.eliminationsPossibles = []
                self.turnsSinceLastCaptureOrMove += 1
                
        
    def actualiser_affichage(self):
        self.canvas.delete("pion")  # supprime uniquement les pions
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
            return  # Numéro invalide
        
        ligne = (num_case - 1) // 5
        colonne = ((num_case - 1) % 5) * 2 + (ligne % 2)

        x1, y1 = colonne * self.taille_case, ligne * self.taille_case
        x2, y2 = x1 + self.taille_case, y1 + self.taille_case

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")

    def colorierCaseOrange(self, num_case):
        if num_case < 1 or num_case > 50:
            return  # Numéro invalide
        
        ligne = (num_case - 1) // 5
        colonne = ((num_case - 1) % 5) * 2 + (ligne % 2)

        x1, y1 = colonne * self.taille_case, ligne * self.taille_case
        x2, y2 = x1 + self.taille_case, y1 + self.taille_case

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="orange", outline="black")
    
    def decolorier_case(self, num_case):
        if num_case < 1 or num_case > 50:
            return  # Numéro invalide
        
        ligne = (num_case - 1) // 5
        colonne = ((num_case - 1) % 5) * 2 + (ligne % 2)

        x1, y1 = colonne * self.taille_case, ligne * self.taille_case
        x2, y2 = x1 + self.taille_case, y1 + self.taille_case

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgrey", outline="black")

    def switch_turn(self):
        if self.turn == 0:
            self.turn = 1
        else:
            self.turn = 0
        self.multiEliminations = False
        self.case_selectionnee = None
        self.deplacementsPossibles = []
        self.eliminationsPossibles = []
        self.actualiser_affichage()
        self.update_turn_label()
        self.update_piece_count()

    def update_turn_label(self):
        if self.turnLabel:
            self.turnLabel.config(text=f"Tour du joueur {'rouge' if self.turn == 1 else 'bleu'}")

    def update_piece_count(self):
        red_count, blue_count = self.plateau.compteurPions()
        self.redCountLabel.config(text=f"Pions rouges: {red_count}")
        self.blueCountLabel.config(text=f"Pions bleus: {blue_count}")
        self.check_victory_or_draw(red_count, blue_count)

    def check_victory_or_draw(self, red_count, blue_count):
        if red_count == 0:
            self.show_message("Victoire du joueur bleu!")
        elif blue_count == 0:
            self.show_message("Victoire du joueur rouge!")
        elif self.noCaptureOrMoveCount >= 25:
            self.show_message("Match nul: 25 coups sans déplacement ni prise.")
        elif self.turnsSinceLastCaptureOrMove >= 16:
            self.check_endgame_draw_conditions()

    def check_endgame_draw_conditions(self):
        red_pieces = [pion for pion in self.plateau.plateau if pion and pion[0] == 1]
        blue_pieces = [pion for pion in self.plateau.plateau if pion and pion[0] == 0]
        
        if self.is_endgame_draw(red_pieces, blue_pieces):
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
        top = Toplevel()
        top.title("Fin de partie")
        msg = Message(top, text=message, font=("Arial", 20))
        msg.pack()
        button = Button(top, text="OK", command=top.destroy)
        button.pack()

    def selection_case(self,x,y):
        num_case= (y-1)*5 + (1-(x%2))*(x//2) + (x%2)*((x//2)+1)
        print(num_case)
        pion = self.plateau.plateau[num_case]
        print(pion)
        if pion is not None:
            joueur, est_dame = pion
            if joueur==1 and self.turn==1:
                self.deplacementsPossibles= self.plateau.deplacementsPossible(num_case)
                print(self.deplacementsPossibles)
                for case_possible in self.deplacementsPossibles:
                    self.colorier_case(case_possible)
    
    def get_plateau(self):
        return self.plateau
    

    
window = DamesJoueurvsJoueur()
window.afficher_plateau()