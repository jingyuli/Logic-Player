import copy
import random
from random import shuffle
from itertools import chain
from sklearn import svm

class Player:
    def __init__(self, myHand, opponents):
        self.hand = myHand
        self.belief = opponents

    def mockUpdateBelief(self, type, player, card, value):
        entropyChange = 0
        if type == True:
            storePossib = copy.deepcopy(self.belief[player][card])
            entropyChange += len(storePossib) - 1
            self.belief[player][card] = [value]
            entropyChange += self.mockRemoveSameCard(player, card, value)
            entropyChange += self.mockImposeLowerCardConstraints(player, card, value)
            entropyChange += self.mockImposeHigherCardConstraints(player, card, value)
            self.belief[player][card] = storePossib
        else:
            entropyChange += 1
            storePossib = copy.deepcopy(self.belief[player][card])
            possibCards = set(storePossib)
            if value in possibCards:
                possibCards.remove(value)
                self.belief[player][card] = list(possibCards)
            entropyChange += self.mockImposeLowerCardConstraints(player, card + 1, (100, 'R'))
            entropyChange += self.mockImposeHigherCardConstraints(player, card - 1, (-100, 'R'))
            self.belief[player][card] = storePossib
        return entropyChange

    def mockRemoveSameCard(self, guessedPlayer, guessedCard, guessedValue):
        for i in range(3):
            if self.belief[i] != 0:
                for j in range(8):
                    if (i != guessedPlayer) or (j != guessedCard):
                        possib = set(self.belief[i][j])
                        entropyChange = len(possib)
                        if guessedValue in possib:
                            possib.remove(guessedValue)
                        possib = list(possib)
                        entropyChange -= len(possib)
        return entropyChange

    def mockImposeHigherCardConstraints(self, guessedPlayer, guessedCard, guessedValue):
        entropyChange = 0
        minPreviousValue, previousColor = guessedValue
        if guessedCard != 7:
            for i in range(guessedCard + 1, 7):
                entropyChange += len(self.belief[guessedPlayer][i])
                currentCard = self.belief[guessedPlayer][i]
                currentColor = currentCard[0][1]
                possible = []
                minCurrentValue = -100
                if currentColor == previousColor:
                    for cardValue, _ in currentCard:
                        if cardValue > minPreviousValue:
                            possible.append((cardValue, currentColor))
                            if cardValue < minCurrentValue:
                                minCurrentValue = cardValue
                else:
                    for cardValue, _ in currentCard:
                        if cardValue >= minPreviousValue:
                            possible.append((cardValue, currentColor))
                            if cardValue < minCurrentValue:
                                minCurrentValue = cardValue
                entropyChange -= len(possible)
                minPreviousValue = minCurrentValue
                previousColor = currentColor
        return entropyChange

    def mockImposeLowerCardConstraints(self, guessedPlayer, guessedCard, guessedValue):
        entropyChange = 0
        maxPreviousValue, previousColor = guessedValue
        if guessedCard != 0:
            for i in range(guessedCard - 1, -1, -1):
                entropyChange += len(self.belief[guessedPlayer][i])
                currentCard = self.belief[guessedPlayer][i]
                currentColor = currentCard[0][1]
                possible = []
                maxCurrentValue = 100
                if currentColor == previousColor:
                    for cardValue, _ in currentCard:
                        if cardValue < maxPreviousValue:
                            possible.append((cardValue, currentColor))
                        if cardValue > maxCurrentValue:
                            maxCurrentValue = cardValue
                else:
                    for cardValue, _ in currentCard:
                        if cardValue <= maxPreviousValue:
                            possible.append((cardValue, currentColor))
                        if cardValue > maxCurrentValue:
                            maxCurrentValue = cardValue
                entropyChange -= len(possible)
                maxPreviousValue = maxCurrentValue
                previousColor = currentColor
        return entropyChange

    def updateBelief(self, type, player, card, value):
        entropyChange = 0
        if type == True:
            entropyChange += len(self.belief[player][card]) - 1
            self.belief[player][card] = [value]
            entropyChange += self.mockRemoveSameCard(player, card, value)
            entropyChange += self.imposeLowerCardConstraints(player, card, value)
            entropyChange += self.imposeHigherCardConstraints(player, card, value)
        else:
            entropyChange += 1
            possibCards = set(self.belief[player][card])
            if value in possibCards:
                possibCards.remove(value)
                self.belief[player][card] = list(possibCards)
            entropyChange += self.imposeLowerCardConstraints(player, card + 1, (100, 'R'))
            entropyChange += self.imposeHigherCardConstraints(player, card - 1, (-100, 'R'))
        return entropyChange

    def imposeHigherCardConstraints(self, guessedPlayer, guessedCard, guessedValue):
        entropyChange = 0
        minPreviousValue, previousColor = guessedValue
        if guessedCard != 7:
            for i in range(guessedCard + 1, 7):
                entropyChange += len(self.belief[guessedPlayer][i])
                currentCard = self.belief[guessedPlayer][i]
                currentColor = currentCard[0][1]
                possible = []
                minCurrentValue = -100
                if currentColor == previousColor:
                    for cardValue, _ in currentCard:
                        if cardValue > minPreviousValue:
                            possible.append((cardValue, currentColor))
                            if cardValue < minCurrentValue:
                                minCurrentValue = cardValue
                else:
                    for cardValue, _ in currentCard:
                        if cardValue >= minPreviousValue:
                            possible.append((cardValue, currentColor))
                            if cardValue < minCurrentValue:
                                minCurrentValue = cardValue
                self.belief[guessedPlayer][i] = possible
                entropyChange -= len(self.belief[guessedPlayer][i])
                minPreviousValue = minCurrentValue
                previousColor = currentColor
        return entropyChange

    def imposeLowerCardConstraints(self, guessedPlayer, guessedCard, guessedValue):
        entropyChange = 0
        maxPreviousValue, previousColor = guessedValue
        if guessedCard != 0:
            for i in range(guessedCard - 1, -1, -1):
                entropyChange += len(self.belief[guessedPlayer][i])
                currentCard = self.belief[guessedPlayer][i]
                currentColor = currentCard[0][1]
                possible = []
                maxCurrentValue = 100
                if currentColor == previousColor:
                    for cardValue, _ in currentCard:
                        if cardValue < maxPreviousValue:
                            possible.append((cardValue, currentColor))
                        if cardValue > maxCurrentValue:
                            maxCurrentValue = cardValue
                else:
                    for cardValue, _ in currentCard:
                        if cardValue <= maxPreviousValue:
                            possible.append((cardValue, currentColor))
                        if cardValue > maxCurrentValue:
                            maxCurrentValue = cardValue
                self.belief[guessedPlayer][i] = possible
                entropyChange -= len(self.belief[guessedPlayer][i])
                maxPreviousValue = maxCurrentValue
                previousColor = currentColor
        return entropyChange

    def removeSameCard(self, guessedPlayer, guessedCard, guessedValue):
        for i in range(3):
            if self.belief[i] != 0:
                for j in range(8):
                    if (i != guessedPlayer) or (j != guessedCard):
                        possib = set(self.belief[i][j])
                        entropyChange = len(possib)
                        if guessedValue in possib:
                            possib.remove(guessedValue)
                        possib = list(possib)
                        entropyChange -= len(possib)
                        self.belief[i][j] = possib
        return entropyChange

    def checkClam(self):
        clam = True
        for i in range(3):
            if self.belief[i] != 0:
                for cards in self.belief[i]:
                    if len(cards) != 1:
                        clam = False
                        break
        return clam

    def revealCard(self):
        if self.hand[0][1] == False:
            return (0, self.hand[0][0])
        elif self.hand[7][1] == False:
            return (7, self.hand[7][0])
        elif self.hand[1][1] == False:
            return (1, self.hand[1][0])
        elif self.hand[6][1] == False:
            return (6, self.hand[6][0])
        elif self.hand[2][1] == False:
            return (2, self.hand[2][0])
        elif self.hand[5][1] == False:
            return (5, self.hand[5][0])
        elif self.hand[3][1] == False:
            return (3, self.hand[3][0])
        elif self.hand[4][1] == False:
            return (4, self.hand[4][0])
        else:
            #print "Uh, someone should have claimed by now probably..."
            return None

    def getFeatures(self):
        hand = self.hand
        belief = self.belief
        features = []
        numRevealed = 0
        for i in range(8):
            if hand[i][1]:
                numRevealed += 1
        features.append(numRevealed)
        for i in range(3):
            if belief[i] !=0:
                for j in range(8):
                    currentCard = belief[i][j]
                    features.append(len(currentCard))
                    minCard = 100
                    maxCard = -100
                    for value, _ in currentCard:
                        if value < minCard:
                            minCard = value
                        if value > maxCard:
                            maxCard = value
                    features.append(minCard)
                    features.append(maxCard)
        return features

class RandomPlayer(Player):
    def __init__(self, myHand, opponents):
        Player.__init__(self, myHand, opponents)

    def chooseMove(self):
        possibleMoves = []
        for i in range(3):
            if self.belief[i] != 0:
                for j in range(8):
                    cards = self.belief[i][j]
                    if len(cards) != 1:
                        possibleMoves.append((i, j))
        chosenPlayer, chosenCard = random.choice(possibleMoves)
        chosenCardGuess = random.choice(self.belief[chosenPlayer][chosenCard])
        return ((chosenPlayer, chosenCard), chosenCardGuess)

class BasicPlayer(Player):
    def __init__(self, myHand, opponents):
        Player.__init__(self, myHand, opponents)

    def chooseMove(self):
        possibleMoves = []
        maxProb = ((0, 0), float('inf'))
        for i in range(3):
            if self.belief[i] != 0:
                for j in range(8):
                    cards = self.belief[i][j]
                    numPossib = len(cards)
                    if numPossib < maxProb and numPossib != 1:
                        maxProb = numPossib

        for i in range(3):
            if self.belief[i] != 0:
                for j in range(8):
                    cards = self.belief[i][j]
                    numPossib = len(cards)
                    if numPossib == maxProb:
                        possibleMoves.append((i, j))

        if len(possibleMoves) == 0:
            possibleMoves.append(maxProb[0])
        chosenPlayer, chosenCard = random.choice(possibleMoves)
        chosenCardGuess = random.choice(self.belief[chosenPlayer][chosenCard])
        return ((chosenPlayer, chosenCard), chosenCardGuess)

class AIPlayer(Player):
    def __init__(self, myHand, opponents, model):
        Player.__init__(self, myHand, opponents)
        self.model = model

    def chooseMove(self):
        X = self.getFeatures()
        cardIndex = int(self.model.predict(X)[0])
        if cardIndex < 8:
            if self.belief[0] != 0:
                guessPlayer, guessCard = (0, cardIndex)
            else:
                guessPlayer, guessCard =  (1, cardIndex)
        else:
            if self.belief[2] != 0:
                guessPlayer, guessCard =  (2, cardIndex - 8)
            else:
                guessPlayer, guessCard =  (1, cardIndex - 8)
        guess = random.choice(self.belief[guessPlayer][guessCard])
        return ((guessPlayer, guessCard), guess)

def verifyClam(clamPlayerIndex, belief, players):
    clam = True
    for i in range(3):
        if i != clamPlayerIndex:
            prediction = belief[i]
            actual = players[i].hand
            for i in range(8):
                if prediction[i][0] != actual[i][0]:
                    clam = False
    return clam

def initGame(AIModel = 0):
    allCards = list(chain.from_iterable(((number, 'R'), (number, 'B')) for number in range(1, 13)))
    shuffle(allCards)

    hand = [zip(sorted(allCards[0:8], key=lambda x: x[0]), [False for i in range(8)]), zip(sorted(allCards[8:16], key=lambda x: x[0]), [False for i in range(8)]), zip(sorted(allCards[16:24], key=lambda x: x[0]), [False for i in range(8)])]
    #print hand

    beliefs = []
    for i in range(3):
        belief = []
        belief.append(zip(range(1, 10), [hand[i][0][0][1] for j in range(9)]))
        belief.append(zip(range(1, 10), [hand[i][1][0][1] for j in range(9)]))
        belief.append(zip(range(2, 11), [hand[i][2][0][1] for j in range(9)]))
        belief.append(zip(range(2, 11), [hand[i][3][0][1] for j in range(9)]))
        belief.append(zip(range(3, 12), [hand[i][4][0][1] for j in range(9)]))
        belief.append(zip(range(3, 12), [hand[i][5][0][1] for j in range(9)]))
        belief.append(zip(range(4, 13), [hand[i][6][0][1] for j in range(9)]))
        belief.append(zip(range(4, 13), [hand[i][7][0][1] for j in range(9)]))
        beliefs.append(belief)

    players = [RandomPlayer(hand[0], [0, beliefs[1], beliefs[2]]), BasicPlayer(hand[1], [beliefs[0], 0 , beliefs[2]]), AIPlayer(hand[2], [beliefs[0], beliefs[1], 0], AIModel)]
    for i in range(3):
        for j in range(8):
            players[i].removeSameCard(i, j, players[i].hand[j][0])
    return playGame(players)

def playGame(players):
    playerIndices = [0, 1, 2]
    shuffle(playerIndices)
    temp = [0, 1, 2]
    iter = 0
    while True:
        iter += 1
        for i in playerIndices:
            currentPlayer = players[i]
            (guessPlayer, guessCard), guess = currentPlayer.chooseMove()
            actual = players[guessPlayer].hand[guessCard][0]
            if guess == actual:
                players[guessPlayer].hand[guessCard] = (actual, True)
                shuffle(temp)
                for j in temp:
                    if j != guessPlayer:
                        if j == i:
                            players[j].updateBelief(True, guessPlayer, guessCard, guess)
                        else:
                            players[j].updateBelief(True, guessPlayer, guessCard, guess)
                    if players[j].checkClam() == True:
                        #print iter
                        if verifyClam(j, players[j].belief, players):
                            #print "Player " + str(j) + " correctly clammed!"
                            #print players[j].belief
                            return (j, True)
                        else:
                            return (j, False)
            else:
                reveal = currentPlayer.revealCard()
                if reveal != None:
                    revealCard, revealValue = reveal
                    currentPlayer.hand[revealCard] = (revealValue, True)
                    shuffle(temp)
                    for j in temp:
                        if j == i:
                            players[j].updateBelief(False, guessPlayer, guessCard, guess)
                        elif j == guessPlayer:
                            players[j].updateBelief(True, i, revealCard, revealValue)
                        else:
                            players[j].updateBelief(False, guessPlayer, guessCard, guess)
                            players[j].updateBelief(True, i, revealCard, revealValue)

                        if players[j].checkClam() == True:
                            #print iter
                            if verifyClam(j, players[j].belief, players):
                                #print "Player " + str(j) + " correctly clammed!"
                                #print players[j].belief
                                return (j, True)
                            else:
                                return (j, False)

def getData(players):
    textFile = open('logicData.txt', 'a')
    playerIndices = [0, 1, 2]
    shuffle(playerIndices)
    temp3 = [0, 1, 2]
    temp8 = range(0, 8)
    iter = 0
    #while nobody has claimed yet
    while True:
        iter += 1
        #players go in a circle taking turns
        for i in playerIndices:
            currentPlayer = players[i]
            belief = currentPlayer.belief
            features = currentPlayer.getFeatures()
            for feature in features:
                textFile.write(str(feature) + ",")
            bestMove = ((0, 0), float('-inf'))
            #different opponents whose cards the current player can guess
            shuffle(temp3)
            for guessPlayer in temp3:
                if belief[guessPlayer] != 0:
                    #can make a guess on any of the 8 cards of an opponent
                    shuffle(temp8)
                    for guessCard in temp8:
                        possibCards = belief[guessPlayer][guessCard]
                        numPossib = len(possibCards)
                        #if we do not already know the card
                        if numPossib != 1:
                            entropyChange = 0
                            #go through different possible guesses for a given card
                            for guess in possibCards:
                                #each different guess leads to different set of features and resulting entropy change in the game
                                possibCards = belief[guessPlayer][guessCard]
                                numPossib = len(possibCards)
                                actual = players[guessPlayer].hand[guessCard][0]
                                if guess == actual:
                                    shuffle(temp3)
                                    for j in temp3:
                                        if j != guessPlayer:
                                            if j == i:
                                                entropyChange += players[j].mockUpdateBelief(True, guessPlayer, guessCard, guess)
                                else:
                                    reveal = currentPlayer.revealCard()
                                    if reveal != None:
                                        revealCard, revealValue = reveal
                                        shuffle(temp3)
                                        for j in temp3:
                                            if j == i:
                                                entropyChange += players[j].mockUpdateBelief(False, guessPlayer, guessCard, guess)
                                            else:
                                                entropyChange -= 0.5 * players[j].mockUpdateBelief(True, i, revealCard, revealValue)

                            entropyChange /= numPossib
                            if entropyChange > bestMove[1]:
                                bestMove = ((guessPlayer, guessCard), entropyChange)
            guessPlayer, guessCard = bestMove[0]
            #matches player, card pair to a single value (a class in terms of training)
            writeIndex = {0: {1: 0, 2: 8}, 1: {0: 0, 2:8}, 2: {0: 0, 1: 8}}
            writeChosenCard = str(writeIndex[i][guessPlayer] + guessCard)
            textFile.write(writeChosenCard + "\n")

            guess = random.choice(currentPlayer.belief[guessPlayer][guessCard])
            #print bestMove
            actual = players[guessPlayer].hand[guessCard][0]
            #print belief
            if guess == actual:
                players[guessPlayer].hand[guessCard] = (actual, True)
                shuffle(temp3)
                for j in temp3:
                    if j != guessPlayer:
                        if j == i:
                            players[j].updateBelief(True, guessPlayer, guessCard, guess)
                        else:
                            players[j].updateBelief(True, guessPlayer, guessCard, guess)
                        if players[j].checkClam() == True:
                            #print iter
                            if verifyClam(j, players[j].belief, players):
                                return (j, True)
                            else:
                                return (j, False)
            else:
                reveal = currentPlayer.revealCard()
                if reveal != None:
                    revealCard, revealValue = reveal
                    currentPlayer.hand[revealCard] = (revealValue, True)
                    shuffle(temp3)
                    for j in temp3:
                        if j == i:
                            players[j].updateBelief(False, guessPlayer, guessCard, guess)
                        elif j == guessPlayer:
                            players[j].updateBelief(True, i, revealCard, revealValue)
                        else:
                            players[j].updateBelief(False, guessPlayer, guessCard, guess)
                            players[j].updateBelief(True, i, revealCard, revealValue)

                        if players[j].checkClam() == True:
                            #print iter
                            if verifyClam(j, players[j].belief, players):
                                return (j, True)
                            else:
                                return (j, False)
            #print belief
    textFile.close()

def trainSVM():
    X = []
    Y = []
    with open('logicData.txt') as dataFile:
        for line in dataFile:
            dataPoint = line.rstrip('\n').split(',')
            numFeatures = len(dataPoint) - 1
            X.append(dataPoint[0:numFeatures])
            Y.append(dataPoint[numFeatures])

    numData = len(Y)
    cardPicker = svm.SVC(gamma=0.001, C=100., kernel = 'sigmoid')
    cardPicker.fit(X, Y)
    correct = 0
    for i in range(numData):
        if cardPicker.predict(X[i]) == Y[i]:
            correct += 1
    print float(correct)/float(numData)
    return cardPicker

def main():
    AIModel = trainSVM()
    wins = {0: 0, 1: 0, 2: 0}
    for i in range(1000):
        player, correct = initGame(AIModel)
        if correct:
            wins[player] += 1
        else:
            wins[player] -= 1
    print wins

#trainSVM()
main()