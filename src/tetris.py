# CREATED BY:
# ▀█████████▄   ▄█          ▄████████ ███    █▄     ▄█   ▄█▄    ▄████████    ▄████████ 
#   ███    ███ ███         ███    ███ ███    ███   ███ ▄███▀   ███    ███   ███    ███ 
#   ███    ███ ███         ███    ███ ███    ███   ███▐██▀     ███    █▀    ███    ███ 
#  ▄███▄▄▄██▀  ███         ███    ███ ███    ███  ▄█████▀     ▄███▄▄▄      ▄███▄▄▄▄██▀ 
# ▀▀███▀▀▀██▄  ███       ▀███████████ ███    ███ ▀▀█████▄    ▀▀███▀▀▀     ▀▀█████▀▀▀   
#   ███    ██▄ ███         ███    ███ ███    ███   ███▐██▄     ███    █▄  ▀█████████▄ 
#   ███    ███ ███▌    ▄   ███    ███ ███    ███   ███ ▀███▄   ███    ███   ███    ███ 
# ▄█████████▀  █████▄▄██   ███    █▀  ████████▀    ███   ▀█▀   ██████████   ███    ███ 
#              ▀                                   ▀                        ███    ███ 2023

import random
import time
import os
import keyboard
from enum import Enum

BOARD_SIZE_X = 10
BOARD_SIZE_Y = 12
COLORS = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫"]

class Movement(Enum):
    DOWN = 1
    RIGHT = 2
    LEFT = 3

class Piece:
    # Init of the class and constructor
    # param in: index -> type of block we will generate (1-numOfBlocks)
    def __init__(self, index: int):
        self.index = index                                  # Type of block (1-7 in this case)
        # ------------------------------------------------- # Position of each individual part of a block
        self.blocks = [[(0,0), (1,0), (2,0), (2,1)],        # [L] block
                       [(0,0), (0,1), (1,0), (1,1)],        # [O] block
                       [(0,0), (0,1), (0,2), (1,1)],        # [T] block
                       [(0,0), (1,0), (2,0), (3,0)],        # [I] block
                       [(0,1), (0,2), (1,0), (1,1)],        # [S] block
                       [(0,0), (0,1), (1,1), (1,2)],        # [Z] block
                       [(0,1), (1,1), (2,1), (2,0)]]        # [J] block
        self.letters = ["L", "O", "T", "I", "S", "Z", "J"]  # "Name" of the blocks
        self.position = self.blocks[index-1]                # Position of the blocks
        self.color = random.randint(1, len(COLORS))         # Random color the block will have               
        self.currRot = 1                                    # Block rotation "level"
    
    # Return how many kind of blocks we have on our game
    def getNumOfBlocks(self):
        return len(self.blocks)
    
    # Return the "name" of the current block
    # param in: index -> index of the current block
    def getLetter(self, index: int) -> str:
        return self.letters[index-1]

    # Update the current rotation value of our block
    def Rotate(self):
        self.currRot += 1
        self.currRot %= 4 #Limit the value between 1-4
    
    # Read the document that contains the rotation matrix from a letter
    # Return the rotation vector our block needs to rotate properly 
    # param in: letter -> letter of the block we want to rotate
    # param in: rotacion -> current rotation of a block
    # param out: rotation vector [(x, x), (x, x), (x, x), (x, x)]
    def ReadRotations(self, letter: str, rotacion: int) -> list:
        file = "src/pieces/" + letter + ".txt"

        with open(file, "r") as f:
            content = f.read()
        
        contents = "\n".join(line.split("#")[0].strip() for line in content.splitlines())
        result = eval(contents)

        return result[rotacion]

class Game:  
    # Init of the class and constructor
    # param in: size_x -> horizontal size of the tetris board
    # param in: size_y -> vertical size of the tetris board  
    def __init__(self, size_x: int, size_y: int):
        self.size_x = size_x                                 # Horizontal size of the board
        self.size_y = size_y                                 # Vertical size of the board
        # The game will have 2 matrix [screens] to handle blocks movement and final block positions
        # Both matrix will be all initialized full of 0's
        # Any value greater than 0 means that there's a block on it
        self.data =   [[0] * size_x for _ in range(size_y)]  # Matrix to handle temporal data like blocks position and movement
        self.matrix = [[0] * size_x for _ in range(size_y)]  # Matrix with the correct final position of the blocks
        self.score = 0                                       # Player score value
    
    # Clean the data-matrix to handle new block positions so blocks wont be overlapped (visually)
    # For that we will asing data-values = matrix-values
    # If we just clean it asinging all values to 0, it will clean the final blocks placed on the bottom too
    # Asinging matrix-values, the final placed blocks will remain
    def Clean(self):
        for i in range(self.size_y):
            for j in range(self.size_x):
                self.data[i][j] = self.matrix[i][j]
    
    # Update the final matrix-values with the temporal data-values
    # This MUST be only called when a block can't go down anymore 
    # [bottom of the screen OR collision with other block]
    def SaveState(self):
        for i in range(self.size_y):
            for j in range(self.size_x):
                self.matrix[i][j] = self.data[i][j]
        # Everytime a block is sucessfully placed, we will check if we have any line
        self.CheckIfLine()
    
    # Check if any horizonrtal line of the board is full of block pieces
    def CheckIfLine(self):
        for i in range(self.size_y):
            aux = 1
            for j in range(self.size_x):
                aux *= self.matrix[i][j] # Multiplying all the values of the line and saving on aux
                # NOTE: each matrix position stores a value from 0-X, if there's any 0, result will be 0.

            # If aux is greater than 0, means that every space of the line if full with a block piece
            if (aux > 0):
                self.UpdateLine(i) # So the line will be updated 
    
    # Delete a full line, add an emplty one on the very top and update score
    # param in: line -> number of the line that will be deleted
    def UpdateLine(self, line: int):
        for i in range(8):
            for j, _ in enumerate(self.data[line]):
                # This is just for visual effects, so the player know which line is completed and deleted
                if (i % 2 == 0):
                    (self.data[line])[j] = 10
                else:
                    (self.data[line])[j] = 11
            time.sleep(0.1)
            self.Print()      
        del self.matrix[line]                      # Delete the line
        self.matrix.insert(0, [0] * self.size_x)   # Add a new empty line on the top
        self.Print()
        self.score += 10

    # Shows the board on the terminal console 
    # Iterating data[][] and print a white emoji if the value is 0 (no block there)
    # Iterating data[][] and print a color emoji if the value is greater than 0 (there's a block there)
    def Print(self):
        os.system("cls")
        for i in range(self.size_y):
            for j in range(self.size_x):
                if (self.data[i][j] == 0): # ------------------------ # No block
                    print("⬜", end="")
                elif (self.data[i][j] >= 0 and self.data[i][j] < 10): # Block (the value is random by piece, so the color too)
                    print(COLORS[self.data[i][j] - 1], end="")

                # This is just for visual effects, so the player know which line is completed and deleted
                elif (self.data[i][j] == 10):
                    print("🔳", end="")
                elif (self.data[i][j] == 11):
                    print("🔲", end="")
            # Printing SCORE 
            if (i == BOARD_SIZE_Y/2 - 1):
                print("     SCORE:", end="")
            if (i == BOARD_SIZE_Y/2):
                print("     " + str(self.score), end="")
            print("\n", end="")
        self.Clean() # Cleaning the screen to update block movement and data

    # Generate a given piece on the [0][0] coords
    # param in: piece: Piece -> piece to generate
    def GeneratePiece(self, piece: Piece):
        for p in piece.position:
            self.data[p[0]][p[1]] = piece.color # Asigning the position and color of the piece to data[][]
        # If the game is not over
        if not self.CheckIfGameOver(piece):
            self.Print()
            # ----- INFINITE PIECE MOVEMENT LOOP ----- #
            while True: 
                key_event = keyboard.read_event()
                cont = True
                if key_event.event_type == keyboard.KEY_DOWN:                # Reading key inputs
                    if key_event.name.lower() == "d":                        # RIGHT movement   
                        piece, desp = self.MovePiece(piece, Movement.RIGHT)  #  └─> Call MovePiece()
                    elif key_event.name.lower() == "a":                      # LEFT movement
                        piece, desp = self.MovePiece(piece, Movement.LEFT)   #  └─> Call MovePiece()
                    elif key_event.name.lower() == "s":                      # DOWM movement
                        piece, cont = self.MovePiece(piece, Movement.DOWN)   #  └─> Call MovePiece()
                    elif key_event.name.lower() == "w":                      # ROTATION movement
                        piece = self.RotatePiece(piece)                      #  └─> Call RotatePiece()

                    if key_event.name.lower() == "esc": # Press [esc] to end the game
                        exit()

                    if not cont: # The loop will end when the piece is placed
                        break
        else:
            self.GameOver()

    # Check if the game can continue
    # param in: piece: Piece -> piece just generated
    # param out: True/False
    def CheckIfGameOver(self, piece: Piece) -> bool:
        gameOver = False
        for p in piece.position:
            # If any block of the piece is generated on another one:
            if (self.matrix[p[0]][p[1]] > 0):
                gameOver = True
                break
        return gameOver

    # Game over screen
    # Iterating data[][] and print a black emoji if the value is 0 (no block there)
    # Iterating data[][] and print a red emoji if the value is greater than 0 (there's a block there)
    def GameOver(self):
        os.system("cls")
        for i in range(self.size_y):
            for j in range(self.size_x):
                if (self.data[i][j] == 0):
                    print("⬛", end="")
                else:
                    print("🟥", end="")
            if (i == BOARD_SIZE_Y/2 - 1):
                print("     GAME OVER:", end="")
            if (i == BOARD_SIZE_Y/2):
                print("     Your score: " + str(self.score), end="")
            print("\n", end="")
        exit(0) # end game

    # Will rotate the given piece if possible
    # Param in:  piece: Piece -> piece to rotate
    # Param out: piece: Piece -> new position of the piece
    def RotatePiece(self, piece: Piece) -> Piece:
        rot = True
        end = False
        newMovement = []
        # Rotation vector the piece needs to rotate 
        vRot = piece.ReadRotations(piece.getLetter(piece.index), piece.currRot-1)
        
        for index, p in enumerate(piece.position):
            p = tuple(x + y for x, y in zip(p, vRot[index])) # Moving each individual block of the piece to new position
            newMovement.append(p)
            # If the new position of the block is outside the screen or in another block:
            if (p[1] >= BOARD_SIZE_X or p[1] < 0 or self.matrix[p[0]][p[1]] > 0):
                rot = False # Can't rotate
                break
            # If the new position of the block is on the end of the screen (placed):
            if (p[0] >= BOARD_SIZE_Y): 
                rot = False # Can't rotate
                end = True
                break
            
        if rot:  # If the block has been able to rotate
            piece.position = newMovement # Update block position
            piece.Rotate()  
        
        for p in piece.position:
            self.data[p[0]][p[1]] = piece.color # Update data[][] with new block
        
        if end:
            self.SaveState()
            return piece
        
        self.Print()
        return piece

    # Will move the given piece if possible
    # Param in:  piece: Piece -> piece to move
    # Param in:  movement     -> type of movement
    # Param out: piece: Piece -> new position of the piece
    # Param out: True/False
    #              └─> True:  The piece is able to move again
    #              └─> False: The piece is placed
    def MovePiece(self, piece: Piece, movement: Movement):
        cont = True
        desp = True
        match movement: # Switch statement (implemented on python 3.10+)
            # THE S KEY HAS BEEN PRESSED
            case Movement.DOWN:
                newMovement = []
                for p in piece.position:
                    p = tuple(x + y for x, y in zip(p, (1, 0))) # Moving each individual block of the piece to new position
                    newMovement.append(p)
                    # If the new position of the block is on the end or above other block (Placed)
                    if (p[0] >= BOARD_SIZE_Y or self.matrix[p[0]][p[1]] > 0):
                        cont = False # Not a valid movement
                        break
                if cont: # Update piece position if the movement is valid
                    piece.position = newMovement
            # THE D KEY HAS BEEN PRESSED
            case Movement.RIGHT:
                newMovement = []
                for p in piece.position:
                    p = tuple(x + y for x, y in zip(p, (0, 1))) # Moving each individual block of the piece to new position
                    newMovement.append(p)
                    if (p[1] >= BOARD_SIZE_X or self.matrix[p[0]][p[1]] > 0):
                        desp = False # Not a valid movement
                        break
                if desp:# Update piece position if the movement is valid 
                    piece.position = newMovement
            # THE A KEY HAS BEEN PRESSED
            case Movement.LEFT:
                newMovement = []
                for p in piece.position:
                    p = tuple(x + y for x, y in zip(p, (0, -1))) # Moving each individual block of the piece to new position
                    newMovement.append(p)
                    if (p[1] < 0 or self.matrix[p[0]][p[1]] > 0):
                        desp = False # Not a valid movement
                        break
                if desp: # Update piece position if the movement is valid
                    piece.position = newMovement
            case _: # It should't be able to happen...
                os.system("cls")
                print("Something weird just happened if you can see this .-.")
                print("Please contact Blauker to report the error")
                exit()
        
        for p in piece.position:
            self.data[p[0]][p[1]] = piece.color # Update data[][] with new block
        
        if not cont:
            self.SaveState()
            return piece, cont
        
        self.Print()
        return piece, cont
        
# ----- START OF THE GAME ----- #
game = Game(BOARD_SIZE_X, BOARD_SIZE_Y)

# INFINITE GAME LOOP generating pieces
while True:
    game.GeneratePiece(Piece(random.randint(1, Piece(1).getNumOfBlocks())))