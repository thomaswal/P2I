class Plateau:
    def __init__(self):
        self.cacheEliminations = []
        self.plateau = [None] * 51  

        #mise en place normal
        # for i in range(1, 21):
        #     self.plateau[i] = (1, False)
        # for i in range(31, 51):
        #     self.plateau[i] = (0, False)
        
        #mise en place test dame et deplacement 
        self.plateau[5] = (1, False)  # Pion joueur 1
        self.plateau[10] = (1, False)  # Pion joueur 1
        self.plateau[15] = (0, False)  # Pion joueur 2
        self.plateau[20] = (0, False)  # Pion joueur 2

        self.plateau[25] = (1, True)  # Dame joueur 1
        self.plateau[30] = (0, True)  # Dame joueur 2

    def __str__(self) -> str:
        return str(self.plateau)
    
    def deplacementBase(self, posPion: int) -> list:
        res = []
        isPairline = (posPion - 1)%10 < 5
        isLeftOutside = posPion%5 == 1 and isPairline
        isRightOutside = posPion%5 == 0 and not isPairline
        isTopOutisde = posPion < 6
        isBottomOutside = posPion > 45
        
        if(self.plateau[posPion] == None): return res
        
        if(self.plateau[posPion][0] == 1):
            #? mouv bas gauche
            if(not isLeftOutside and not isBottomOutside):
                possiblePos = posPion + 4 if isPairline else posPion + 5
                res.append(possiblePos)
            #? moiv bas droite
            if(not isRightOutside and not isBottomOutside):
                possiblePos = posPion + 5 if isPairline else posPion + 6
                res.append(possiblePos)
        if(self.plateau[posPion][0] == 0 ):
            #? mouv haut gauche
            if(not isLeftOutside and not isTopOutisde):
                possiblePos = posPion - 6 if isPairline else posPion - 5
                res.append(possiblePos)
            #? mouv haut droit
            if(not isRightOutside and not isTopOutisde):
                possiblePos = posPion - 5 if isPairline else posPion - 4
                res.append(possiblePos)

        #mouv dames :

        return res
    
    def eliminationBas(self, posPion: int) -> list:
        res = []
        isPairline = (posPion - 1)%10 < 5
        isLeftOutside = posPion%5 == 1 and isPairline
        isRightOutside = posPion%5 == 0 and not isPairline
        isTopOutisde = posPion < 6
        isBottomOutside = posPion > 45

        if(self.plateau[posPion] == None): return res
        
        if(self.plateau[posPion][0] == 0):
            #? mouv bas gauche
            if(not isLeftOutside and not isBottomOutside):
                possiblePos = posPion + 4 if isPairline else posPion + 5
                res.append(possiblePos)
            #? moiv bas droite
            if(not isRightOutside and not isBottomOutside):
                possiblePos = posPion + 5 if isPairline else posPion + 6
                res.append(possiblePos)
        if(self.plateau[posPion][0] == 1):
            #? mouv haut gauche
            if(not isLeftOutside and not isTopOutisde):
                possiblePos = posPion - 6 if isPairline else posPion - 5
                res.append(possiblePos)
            #? mouv haut droit
            if(not isRightOutside and not isTopOutisde):
                possiblePos = posPion - 5 if isPairline else posPion - 4
                res.append(possiblePos)

                # actuellemtn res = 2 cases en arreire: verifier si le manger et possible !!!!!!
        return res
    
    def eliminationPossible(self, pos1: int, pos2: int) -> tuple:
        res = None
        if(self.plateau[pos2] == None): return None
        if(self.plateau[pos1][0] == self.plateau[pos2][0]): return None
        isPairline = (pos1 - 1)%10 < 5
        isPairline2 = (pos2 - 1)%10 < 5
        isUpward = pos1 > pos2
        isRight = False
        if(isUpward) :
            isRight = pos1 == pos2 + 5 if isPairline else pos1 == pos2 + 4
            if(isRight):
                isRightOutside = pos2%5 == 0 and not isPairline2
                finalPos = pos1 - 9
                isOutside = finalPos <= 0 or isRightOutside
                if not isOutside and self.plateau[finalPos] == None : return (finalPos, pos2)
            else:
                isLeftOutside = pos2%5 == 1 and isPairline2
                finalPos = pos1 - 11
                isOutside = finalPos <= 0 or isLeftOutside
                if not isOutside and self.plateau[finalPos] == None : return (finalPos, pos2)
        else:
            isRight = pos1 == pos2 - 5 if isPairline else pos1 == pos2 - 6
            if(isRight):
                isRightOutside = pos2%5 == 0 and not isPairline2
                finalPos = pos1 + 11
                isOutside = finalPos > 50 or isRightOutside
                if not isOutside and self.plateau[finalPos] == None : return (finalPos, pos2)
            else:
                isLeftOutside = pos2%5 == 1 and isPairline2
                finalPos = pos1 + 9
                isOutside = finalPos > 50 or isLeftOutside
                if not isOutside and self.plateau[finalPos] == None : return (finalPos, pos2)
        return None
    
    def eliminationsPossibles(self, posPion: int) -> list:
        res =[]
        bas = self.eliminationBas(posPion)
        haut = self.deplacementBase(posPion)
        for i in bas:
            elimination = self.eliminationPossible(posPion, i)
            if elimination != None:
                res.append(elimination[0])
                self.cacheEliminations.append((elimination[0],elimination[1]))
        for i in haut:
            elimination = self.eliminationPossible(posPion, i)
            if elimination != None:
                res.append(elimination[0])  
                self.cacheEliminations.append((elimination[0],elimination[1]))
        return res
                

    def deplacementsPossible(self, posPion: int) -> list:
        res = []
        baseDeplacements = self.deplacementBase(posPion)
        for deplacement in baseDeplacements:
            if self.plateau[deplacement] == None:
                res.append(deplacement)         
        return res
    
    def deplacer(self, posPion: int, newPos: int):
        if newPos in self.deplacementsPossible(posPion) or newPos in self.deplacementDamesPossible(posPion)[0]:
            sauvegardePosition = self.plateau[posPion]
            self.plateau[posPion] = None
            self.plateau[newPos] = sauvegardePosition

            # transfo en dame
            if (newPos <6 and self.plateau[newPos][0] == 0) or (newPos > 45 and self.plateau[newPos][0] == 1):
                self.plateau[newPos] = (self.plateau[newPos][0], True)
                print("Dame !", newPos)


    
    def eliminer(self, posPion: int, newPos: int):
        if newPos in self.eliminationsPossibles(posPion) or newPos in self.deplacementDamesPossible(posPion)[1]: 
            sauvegardePosition = self.plateau[posPion]
            self.plateau[posPion] = None
            self.plateau[newPos] = sauvegardePosition        
            for elimination in self.cacheEliminations:
                    if elimination[0] == newPos:
                        self.plateau[elimination[1]] = None
                        self.cacheEliminations=[]
                        break           

    def getPlateau(self):
        return self.plateau
    

    def deplacementDamesPossible(self,posPion):
        deplacementsPossibles = []
        eliminationsPossibles = []
        isPairline = (posPion - 1)%10 < 5
        diagDroiteHaut=[]
        diagDroiteBas=[]
        diagGaucheHaut=[]
        diagGaucheBas=[]
        i = posPion
        isLeftOutside = i%5 == 1 and isPairline
        isRightOutside = i%5 == 0 and not isPairline
        while i <=50 and not isRightOutside:
            diagDroiteHaut.append(i)
            isPairline = (i - 1)%10 < 5
            if isPairline:    
                i+=5
            else:
                i+=6
            isPairline = (i - 1)%10 < 5
            isRightOutside = i%5 == 0 and not isPairline
            if isRightOutside and i<=50:
                diagDroiteHaut.append(i)
        i = posPion
        while i >0 and not isLeftOutside    :
            diagGaucheBas.append(i)
            isPairline = (i - 1)%10 < 5
            if isPairline:    
                i-=6
            else:
                i-=5
            isPairline = (i - 1)%10 < 5
            isLeftOutside = i%5 == 1 and isPairline
            if isLeftOutside and i>0:
                diagGaucheBas.append(i)
        i = posPion
        isPairline = (i - 1)%10 < 5
        isLeftOutside = i%5 == 1 and isPairline
        while i <=50 and not isLeftOutside:
            diagGaucheHaut.append(i)
            isPairline = (i - 1)%10 < 5
            if isPairline:    
                i+=4
            else:
                i+=5
            isPairline = (i - 1)%10 < 5
            isLeftOutside = i%5 == 1 and isPairline
            if isLeftOutside and i<=50:
                diagGaucheHaut.append(i)
        i = posPion
        isPairline = (i - 1)%10 < 5
        isRightOutside = i%5 == 0 and not isPairline
        while i >0 and not isRightOutside:
            diagDroiteBas.append(i)
            isPairline = (i - 1)%10 < 5
            if isPairline:    
                i-=5
            else:
                i-=4
            isPairline = (i - 1)%10 < 5
            isRightOutside = i%5 == 0 and not isPairline
            if isRightOutside and i>0:
                diagDroiteBas.append(i)

        #ici on a la pos de toute les diagonal manque a verif si on peut deplacer ou manger 
        diagonales=[diagGaucheBas,diagDroiteBas,diagGaucheHaut,diagDroiteHaut]
        for diag in diagonales:
            stop = False
            if diag !=[posPion]:
                for i in range(1,len(diag)):
                    if self.plateau[diag[i]] != None and stop == False:
                        if self.plateau[diag[i]][0] == self.plateau[posPion][0]: #si pion allié fin 
                            stop = True
                        if self.plateau[diag[i]][0] != self.plateau[posPion][0]: #si pion ennemi test elimination
                            sauvegarde = self.plateau[diag[i-1]]
                            self.plateau[diag[i-1]]=self.plateau[posPion]
                            elimination = self.eliminationPossible(diag[i-1], diag[i])
                            self.plateau[diag[i-1]]= sauvegarde
                            if elimination == None:
                                stop = True
                            else:
                                eliminations = diag[i+1:]
                                print(eliminations)
                                kill=diag[i]
                                print(kill)
                                for j in range(len(eliminations)):
                                    if self.plateau[eliminations[j]] == None:
                                        eliminationsPossibles.append(eliminations[j])
                                        self.cacheEliminations.append((eliminations[j],kill))
                                        stop = True
                                    else:
                                        stop = True
                                        break
                    if self.plateau[diag[i]] == None and stop == False:
                        deplacementsPossibles.append(diag[i])


        return deplacementsPossibles,eliminationsPossibles

    def compteurPions(self):
        nombre_pions_joueur_1 = 0
        nombre_pions_joueur_2 = 0
        for pion in self.plateau:
            if pion is not None:
                joueur, _ = pion
                if joueur == 1:
                    nombre_pions_joueur_1 += 1
                elif joueur == 0:
                    nombre_pions_joueur_2 += 1
        return nombre_pions_joueur_1, nombre_pions_joueur_2


