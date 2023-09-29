# CREATED BY:
# ▀█████████▄   ▄█          ▄████████ ███    █▄     ▄█   ▄█▄    ▄████████    ▄████████ 
#   ███    ███ ███         ███    ███ ███    ███   ███ ▄███▀   ███    ███   ███    ███ 
#   ███    ███ ███         ███    ███ ███    ███   ███▐██▀     ███    █▀    ███    ███ 
#  ▄███▄▄▄██▀  ███         ███    ███ ███    ███  ▄█████▀     ▄███▄▄▄      ▄███▄▄▄▄██▀ 
# ▀▀███▀▀▀██▄  ███       ▀███████████ ███    ███ ▀▀█████▄    ▀▀███▀▀▀     ▀▀█████▀▀▀   
#   ███    ██▄ ███         ███    ███ ███    ███   ███▐██▄     ███    █▄  ▀█████████▄ 
#   ███    ███ ███▌    ▄   ███    ███ ███    ███   ███ ▀███▄   ███    ███   ███    ███ 
# ▄█████████▀  █████▄▄██   ███    █▀  ████████▀    ███   ▀█▀   ██████████   ███    ███ 
#              ▀                                   ▀                        ███    ███ 

import random
import time
from enum import Enum
import os
import keyboard

BOARD_SIZE_X = 10
BOARD_SIZE_Y = 12

class Movement(Enum):
    DOWN = 1
    RIGHT = 2
    LEFT = 3

class Piece:
    def __init__(self, index: int):
        self.index = index
        self.blocks = [[(0,0), (1,0), (2,0), (2,1)], # L
                       [(0,0), (0,1), (1,0), (1,1)], # O
                       [(0,0), (0,1), (0,2), (1,1)], # T
                       [(0,0), (1,0), (2,0), (3,0)], # I
                       [(0,1), (0,2), (1,0), (1,1)], # S
                       [(0,0), (0,1), (1,1), (1,2)], # Z
                       [(0,1), (1,1), (2,1), (2,0)]] # J
        self.letters = ["L", "O", "T", "I", "S", "Z", "J"]
        self.position = self.blocks[index-1]
        self.color = random.randint(1, 7)
        self.currRot = 1
    
    def getNumOfBlocks(self):
        return len(self.blocks)
    
    def getLetter(self, index: int) -> str:
        return self.letters[index-1]

    def Rotate(self):
        self.currRot += 1
        self.currRot %= 4
    
    def ReadRotations(self, letter: str, rotacion: int) -> list:
        file = "pieces/" + letter + ".txt"

        with open(file, "r") as f:
            content = f.read()
        
        contents = "\n".join(line.split("#")[0].strip() for line in content.splitlines())
        result = eval(contents)

        return result[rotacion]

class Screen:  
    def __init__(self, size_x: int, size_y: int):
        self.size_x = size_x
        self.size_y = size_y
        self.data = [[0] * size_x for _ in range(size_y)]
        self.matrix = [[0] * size_x for _ in range(size_y)]
        self.score = 0
    
    def Clean(self):
        for i in range(self.size_y):
            for j in range(self.size_x):
                self.data[i][j] = self.matrix[i][j]
    
    def SaveState(self):
        for i in range(self.size_y):
            for j in range(self.size_x):
                self.matrix[i][j] = self.data[i][j]
        
        self.CheckIfLine()
    
    def CheckIfLine(self):
        for i in range(self.size_y):
            aux = 1
            for j in range(self.size_x):
                aux *= int(self.matrix[i][j])
            
            if (aux > 0):
                self.UpdateLines(i)
    
    def UpdateLines(self, line: int):
        for i in range(8):
            for j, _ in enumerate(self.data[line]):
                # print("(self.data[line])[2]", (self.data[line])[j])
                if (i % 2 == 0):
                    (self.data[line])[j] = 10
                else:
                    (self.data[line])[j] = 11
            time.sleep(0.1)
            self.Print()      
        del self.matrix[line]
        self.matrix.insert(0, [0] * self.size_x)
        self.Print()
        self.score += 10

    def Print(self):
        os.system("cls")
        for i in range(self.size_y):
            for j in range(self.size_x):
                if (self.data[i][j] == 0):
                    print("⬜", end="")
                elif (self.data[i][j] == 1):
                    print("🟥", end="")
                elif (self.data[i][j] == 2):
                    print("🟧", end="")
                elif (self.data[i][j] == 3):
                    print("🟨", end="")
                elif (self.data[i][j] == 4):
                    print("🟩", end="")
                elif (self.data[i][j] == 5):
                    print("🟦", end="")
                elif (self.data[i][j] == 6):
                    print("🟪", end="")
                elif (self.data[i][j] == 7):
                    print("🟫", end="")
                elif (self.data[i][j] == 10):
                    print("🔳", end="")
                elif (self.data[i][j] == 11):
                    print("🔲", end="")
            if (i == 5):
                print("     SCORE:", end="")
            if (i == 6):
                print("     " + str(self.score), end="")
            print("\n", end="")
        self.Clean()

    def GeneratePiece(self, piece: Piece):
        for p in piece.position:
            self.data[p[0]][p[1]] = piece.color
        
        if not self.CheckIfGameOver(piece):
            self.Print()
            while True:
                key_event = keyboard.read_event()
                cont = True
                if key_event.event_type == keyboard.KEY_DOWN:
                    if key_event.name.lower() == "d":
                        piece, desp = self.MovePiece(piece, Movement.RIGHT)
                    elif key_event.name.lower() == "a":
                        piece, desp = self.MovePiece(piece, Movement.LEFT)
                    elif key_event.name.lower() == "s":
                        piece, cont = self.MovePiece(piece, Movement.DOWN)
                    elif key_event.name.lower() == "w":
                        piece, rot = self.RotatePiece(piece)

                    if key_event.name.lower() == "q":
                        exit()

                    if not cont:
                        break
        else:
            self.GameOver()

    def CheckIfGameOver(self, piece: Piece) -> bool:
        gameOver = False
        for p in piece.position:
            if (self.matrix[p[0]][p[1]] > 0):
                gameOver = True
                break
        return gameOver

    def GameOver(self):
        os.system("cls")
        for i in range(self.size_y):
            for j in range(self.size_x):
                if (self.data[i][j] == 0):
                    print("⬛", end="")
                else:
                    print("🟥", end="")
            if (i == 5):
                print("     GAME OVER:", end="")
            if (i == 6):
                print("     Your score: " + str(self.score), end="")
            print("\n", end="")
        exit(0)

    def RotatePiece(self, piece: Piece):
        rot = True
        end = True
        newMovement = []
        vRot = piece.ReadRotations(piece.getLetter(piece.index), piece.currRot-1)
        
        for index, p in enumerate(piece.position):
            p = tuple(x + y for x, y in zip(p, vRot[index]))
            newMovement.append(p)

            if (p[1] >= BOARD_SIZE_X or p[1] < 0 or self.matrix[p[0]][p[1]] > 0):
                rot = False
                break
            if (p[0] >= BOARD_SIZE_Y):
                rot = False
                end = False
                break
            
        if rot:
            piece.position = newMovement
            piece.Rotate()  
        
        for p in piece.position:
            self.data[p[0]][p[1]] = piece.color
        
        if not end:
            self.SaveState()
            return piece, end
        
        self.Print()
        return piece, rot


    def MovePiece(self, piece: Piece, movement: Movement):
        cont = True
        desp = True
        match movement:
            case Movement.DOWN:
                newMovement = []
                for p in piece.position:
                    p = tuple(x + y for x, y in zip(p, (1, 0)))
                    newMovement.append(p)
                    if (p[0] >= BOARD_SIZE_Y or self.matrix[p[0]][p[1]] > 0):
                        cont = False
                        break
                if cont:   
                    piece.position = newMovement
            
            case Movement.RIGHT:
                newMovement = []
                for p in piece.position:
                    p = tuple(x + y for x, y in zip(p, (0, 1)))
                    newMovement.append(p)
                    if (p[1] >= BOARD_SIZE_X or self.matrix[p[0]][p[1]] > 0):
                        desp = False
                        break
                if desp:   
                    piece.position = newMovement
            
            case Movement.LEFT:
                newMovement = []
                for p in piece.position:
                    p = tuple(x + y for x, y in zip(p, (0, -1)))
                    newMovement.append(p)
                    if (p[1] < 0 or self.matrix[p[0]][p[1]] > 0):
                        desp = False
                        break
                if desp:   
                    piece.position = newMovement

            case _:
                print("default action")
        
        for p in piece.position:
            self.data[p[0]][p[1]] = piece.color
        
        if not cont:
            self.SaveState()
            return piece, cont
        
        self.Print()
        return piece, cont
        

screen = Screen(BOARD_SIZE_X, BOARD_SIZE_Y)
while True:
    screen.GeneratePiece(Piece(random.randint(1, Piece(1).getNumOfBlocks())))