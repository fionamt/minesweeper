from graphics import *
import random

__author__ = 'Alex'

class graphicMinesweeperBoard:
    random.seed()
    def __init__(self, rows, cols, mines):
        self.flag = False
        self.numFlag = 0
        self.numMine = mines
        self.board = GraphWin('Minesweeper',(cols + 2)*30, (rows + 2)*30)
        self.squares = [[None for x in range(rows)]for x in range(cols)]
        self.mines = [[0 for x in range(rows)]for x in range(cols)]
        self.numNeighbors =[[0 for x in range(rows)]for x in range(cols)]
        self.flagButton = Circle(Point(20, 20),10)
        self.flagButton.setFill('red')
        self.flagButton.draw(self.board)
        flagMessage = Text(Point(50, 20), 'Flag?')
        flagMessage.setSize(15)
        flagMessage.draw(self.board)
        for i in range(cols):
            for j in range(rows):
                rect = Rectangle(Point((i+1) * 30, (j+1)*30), Point((i+2)*30, (j+2)*30))
                rect.setFill('blue')
                rect.draw(self.board)
                self.squares[i][j] = rect
        for mine in range(mines):
            row = random.randint(0, rows -1)
            col = random.randint(0, cols - 1)
            if col + 1 < len(self.numNeighbors):
                self.numNeighbors[col + 1][row] += 1
                if row-1 >=0:
                    self.numNeighbors[col + 1][row-1] +=1
                if row + 1 < len(self.numNeighbors[col]):
                    self.numNeighbors[col + 1][row + 1] += 1
            if col - 1 >=0:
                self.numNeighbors[col - 1][row] += 1
                if row -1 >=0:
                    self.numNeighbors[col -1][row-1] += 1
                if row + 1 < len(self.numNeighbors[col]):
                    self.numNeighbors[col -1][row + 1] +=1
            if row + 1 < len(self.numNeighbors[col]):
                self.numNeighbors[col][row + 1] += 1
            if row -1 >= 0:
                self.numNeighbors[col][row -1] += 1
            self.mines[col][row] = 1

    def playGame(self):
        lose = False
        while not lose:
            if self.numFlag == self.numMine:
                message = Text(Point(self.board.getWidth()/2, self.board.getHeight()/2), "You win!!")
                message.setSize(30)
                message.setFill('black')
                message.draw(self.board)
                self.board.getMouse()
                self.board.close()
                break
            clickLoc = self.board.getMouse()
            if clickLoc.getX() < 30 and clickLoc.getY() < 30:
                if self.flag == True:
                    self.flagButton.setFill('red')
                    self.flag = False
                else:
                    self.flagButton.setFill('green')
                    self.flag = True
            else:
                col = (clickLoc.getX()/30)-1
                row = (clickLoc.getY()/30)-1
                if col >=0 and col < len(self.squares) and row >=0 and row <= len(self.squares[col]):
                    if self.mines[col][row] == 1 and self.flag == False:
                        self.squares[col][row].setFill('red')
                        lose = True
                    elif self.mines[col][row] == 0 and self.flag == False:
                        self.squares[col][row].setFill('white')
                        self.mines[col][row] = 3
                        message = Text(Point((col+1) * 30 + 15, (row+1)*30 + 15), self.numNeighbors[col][row])
                        message.setSize(12)
                        message.draw(self.board)
                    elif self.flag == True:
                        self.squares[col][row].setFill('green')
                        if self.mines[col][row] == 1:
                            self.numFlag += 1
                            self.mines[col][row] = 2
                        elif self.mines[col][row] == 2:
                            self.squares[col][row].setFill('blue')
                            self.numFlag -= 1
                            self.mines[col][row] = 1
                        elif self.mines[col][row] == 0:
                            self.mines[col][row] = 4
                        elif self.mines[col][row] == 4:
                            self.mines[col][row] = 0
                            self.squares[col][row].setFill('blue')
        if lose == True:
            message = Text(Point(self.board.getWidth()/2, self.board.getHeight()/2), "You lose!!")
            message.setSize(30)
            message.setFill('black')
            message.draw(self.board)
            self.board.getMouse()
            self.board.close()

def main():
    rows = 0
    cols = 0
    mines = 0
    while rows <= 1 or rows > 16:
        rows = input("Input number of rows on board <= 16: ")
        if rows <= 1 or rows > 16:
            print "Please ensure your value is within the given constraints..."
    while cols <= 1 or cols > 30:
        cols = input("Input number of columns on board <= 30: ")
        if cols <= 1 or cols > 30:
           print "Please ensure your value is within the given constraints..."
    while mines < 1 or mines > 99:
        mines = input("Input number of mines on board <= 99: ")
        if mines < 1 or mines > 99:
            print "Please ensure your value is within the given constraints..."
    board = graphicMinesweeperBoard(rows, cols, mines)
    board.playGame()

main()
