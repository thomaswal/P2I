from tkinter import *
from Plateau import Plateau

class GraphiquePlateau:
    def __init__(self):
        self.plateau = Plateau()
        self.listeRect = []
        self.deplacementsPossibles = []
        self.canvas = None
        self.listePions = []
        self.turn = 1
        self.turnLabel = None
        self.taille_case=50
        self.case_selectionnee = None 

    def afficher_plateau(self):
        fenetre = Tk()
        fenetre.title("Jeu de Dames")
        fenetre.geometry("600x600")

        if self.turn==1:
            self.turnLabel = Label(fenetre, text="Tour du joueur rouge ", font=("Arial", 20))
            self.turnLabel.pack()
        else :
            self.turnLabel = Label(fenetre, text="Tour du joueur bleu", font=("Arial", 20))
            self.turnLabel.pack()

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
                    self.deplacementsPossibles = self.plateau.deplacementsPossible(num_case)
                    if self.deplacementsPossibles == []: #selection d'un pion que si il peut bouger
                        self.case_selectionnee = None
                    else:
                        self.case_selectionnee = num_case 

                    for case_possible in self.deplacementsPossibles:
                        self.colorier_case(case_possible)  # colorer les cases où il peut aller
                    print(f"Pion sélectionné : {num_case}, déplacements possibles : {self.deplacementsPossibles}")

        else:  # Deuxième clic 
            if num_case in self.deplacementsPossibles:
                for case_possible in self.deplacementsPossibles:
                        self.decolorier_case(case_possible)  #efface les cases
                self.plateau.deplacer(self.case_selectionnee,num_case) #deplacement sur la plateau
                self.actualiser_affichage() 
                print(f"Pion déplacé de {self.case_selectionnee} à {num_case}. Tour du joueur {'bleu' if self.turn == 1 else 'rouge'}.")
                if self.turn==0 :
                    self.turn = 1 
                else :
                    self.turn = 0     

            else:
                for case_possible in self.deplacementsPossibles:
                        self.decolorier_case(case_possible) 
                
            self.case_selectionnee = None
            self.deplacementsPossibles = []
        
    def actualiser_affichage(self):
        self.canvas.delete("pion")  # supprime uniquement les pions
        print('pions supr')

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


        
    def colorier_case(self, num_case):
        if num_case < 1 or num_case > 50:
            return  # Numéro invalide
        
        ligne = (num_case - 1) // 5
        colonne = ((num_case - 1) % 5) * 2 + (ligne % 2)

        x1, y1 = colonne * self.taille_case, ligne * self.taille_case
        x2, y2 = x1 + self.taille_case, y1 + self.taille_case

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
    
    def decolorier_case(self, num_case):
        if num_case < 1 or num_case > 50:
            return  # Numéro invalide
        
        ligne = (num_case - 1) // 5
        colonne = ((num_case - 1) % 5) * 2 + (ligne % 2)

        x1, y1 = colonne * self.taille_case, ligne * self.taille_case
        x2, y2 = x1 + self.taille_case, y1 + self.taille_case

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgrey", outline="black")



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

                




    


window = GraphiquePlateau()
window.afficher_plateau()