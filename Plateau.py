class Plateau:
    def __init__(self):
        self.cacheEliminations = []
        self.plateau = [None] * 51
        for i in range(1, 21):
            self.plateau[i] = (1, False)
        for i in range(31, 51):
            self.plateau[i] = (0, False)

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
        
        if(self.plateau[posPion][0] == 1 or self.plateau[posPion][1]):
            #? mouv bas gauche
            if(not isLeftOutside and not isBottomOutside):
                possiblePos = posPion + 4 if isPairline else posPion + 5
                res.append(possiblePos)
            #? moiv bas droite
            if(not isRightOutside and not isBottomOutside):
                possiblePos = posPion + 5 if isPairline else posPion + 6
                res.append(possiblePos)
        if(self.plateau[posPion][0] == 0 or self.plateau[posPion][1]):
            #? mouv haut gauche
            if(not isLeftOutside and not isTopOutisde):
                possiblePos = posPion - 6 if isPairline else posPion - 5
                res.append(possiblePos)
            #? mouv haut droit
            if(not isRightOutside and not isTopOutisde):
                possiblePos = posPion - 5 if isPairline else posPion - 4
                res.append(possiblePos)
        return res
    
    # def eliminationBas(self, posPion: int) -> list:
    #     res = []
    #     isPairline = (posPion - 1)%10 < 5
    #     isLeftOutside = posPion%5 == 1 and isPairline
    #     isRightOutside = posPion%5 == 0 and not isPairline
    #     isTopOutisde = posPion < 6
    #     isBottomOutside = posPion > 45

    #     if(self.plateau[posPion] == None): return res
        
    #     if(self.plateau[posPion][0] == 1 or self.plateau[posPion][1]):
    #         #? mouv bas gauche
    #         if(not isLeftOutside and not isBottomOutside):
    #             possiblePos = posPion + 4 if isPairline else posPion + 5
    #             res.append(possiblePos)
    #         #? moiv bas droite
    #         if(not isRightOutside and not isBottomOutside):
    #             possiblePos = posPion + 5 if isPairline else posPion + 6
    #             res.append(possiblePos)
    #     if(self.plateau[posPion][0] == 0 or self.plateau[posPion][1]):
    #         #? mouv haut gauche
    #         if(not isLeftOutside and not isTopOutisde):
    #             possiblePos = posPion - 6 if isPairline else posPion - 5
    #             res.append(possiblePos)
    #         #? mouv haut droit
    #         if(not isRightOutside and not isTopOutisde):
    #             possiblePos = posPion - 5 if isPairline else posPion - 4
    #             res.append(possiblePos)
    #     return res
    
    def eliminationPossible(self, pos1: int, pos2: int) -> tuple:
        res = None
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
    
    def deplacementsPossible(self, posPion: int) -> list:
        res = []
        self.cacheEliminations = []
        baseDeplacements = self.deplacementBase(posPion)
        for deplacement in baseDeplacements:
            if self.plateau[deplacement] == None:
                res.append(deplacement)
            else:
                elimination = self.eliminationPossible(posPion, deplacement)
                if elimination != None:
                    self.plateau[elimination[0]] = self.plateau[posPion]
                    baseDeplacements2 = self.deplacementBase(elimination[0])
                    self.plateau[elimination[0]] = None
                    print(baseDeplacements2) 
                    for deplacement2 in baseDeplacements2:
                        if self.plateau[deplacement2] == None:
                            self.cacheEliminations.append((elimination[0],elimination[1],1))
                            res.append(elimination[0])
                        else:
                            self.plateau[elimination[0]] = self.plateau[posPion]
                            elimination2 = self.eliminationPossible(elimination[0], deplacement2)
                            if elimination2 != None:
                                self.cacheEliminations.append((elimination2[0],(elimination2[1],elimination[1]),2))
                                res.append(elimination2[0])                                           
                            else:
                                self.cacheEliminations.append((elimination[0],elimination[1],1))
                                res.append(elimination[0])
                            self.plateau[elimination[0]] = None 

                    
        return res
    
    def deplacer(self, posPion: int, newPos: int):
        if newPos in self.deplacementsPossible(posPion):
            sauvegardePosition = self.plateau[posPion]
            self.plateau[posPion] = None
            self.plateau[newPos] = sauvegardePosition
            

            dame = None
            elimination = None

            #? Transformation en dame
            if (newPos in range(1, 6) and self.plateau[newPos][0] == 0) or (newPos in range(46, 51) and self.plateau[newPos][0] == 1):
                self.plateau[newPos] = (self.plateau[newPos][0], True)
                print("Dame !", newPos)
                dame = newPos

            #? Elimination 1 case
            for elimination in self.cacheEliminations:
                if elimination[2]==1:
                    if elimination[0] == newPos:
                        self.plateau[elimination[1]] = None
                        print('Elimination !')
                        print('pion restants: ', self.plateau.count((0, False)) + self.plateau.count((1, False)))
                        elimination = elimination[1]
                        break

                if elimination[2]==2:
                    if elimination[0] == newPos:
                        self.plateau[elimination[1][0]] = None
                        self.plateau[elimination[1][1]] = None
                        print('Elimination double !')
                        print('pion restants: ', self.plateau.count((0, False)) + self.plateau.count((1, False)))
                        elimination = elimination[1]
                        break
        
            return (dame, elimination)
        
        
    def getPlateau(self):
        return self.plateau
