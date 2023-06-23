import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from Checkers import Checkers, Positions
from enum import Enum

window = tk.Tk()
window.title("Checkers")
IMG_SIZE = 60
black_man_img = ImageTk.PhotoImage(Image.open('assets/black_man.png').resize((IMG_SIZE, IMG_SIZE)))
black_king_img = ImageTk.PhotoImage(Image.open('assets/black_king.png').resize((IMG_SIZE, IMG_SIZE)))
white_man_img = ImageTk.PhotoImage(Image.open('assets/white_man.png').resize((IMG_SIZE, IMG_SIZE)))
white_king_img = ImageTk.PhotoImage(Image.open('assets/white_king.png').resize((IMG_SIZE, IMG_SIZE)))
blank_img = ImageTk.PhotoImage(Image.open('assets/blank.png').resize((IMG_SIZE, IMG_SIZE)))

difficulty = tk.IntVar()
message = tk.StringVar()


class Mode(Enum):
    SINGLE_PLAYER = 0
    MULTIPLE_PLAYER = 1
class Algorithm(Enum):
    MINIMAX = 0
    RANDOM = 1

CHECKER_SIZE = 8
# GAME_MODE = Mode.SINGLE_PLAYER
GAME_MODE = Mode.SINGLE_PLAYER
STARTING_PLAYER = Checkers.BLACK
USED_ALGORITHM = Algorithm.MINIMAX
EVALUATION_FUNCTION = Checkers.evaluate2

class GUI:
    
    def __init__(self) -> None:
        super().__init__()
        self.game = Checkers(CHECKER_SIZE)
        self.history = [self.game.getBoard()]
        self.historyPtr = 0
        difficulty.set(4)
        # Set up the message area and difficulty slider
        panel = tk.Frame(master=window, borderwidth=7)
        widget = tk.Scale(master=panel, variable=difficulty, orient=tk.HORIZONTAL, from_=1, to=5)
        widget.pack(side=tk.RIGHT)
        label = tk.Label(master=panel, text="         ")
        label.pack(side=tk.RIGHT)
        label = tk.Label(master=panel, textvariable=message, width=20, bg="seashell")
        label.pack(side=tk.RIGHT)
        panel.pack()

        # Change difficulty with depth
        self.maxDepth = difficulty.get()

        self.player = STARTING_PLAYER
        if self.player == Checkers.WHITE and GAME_MODE == Mode.SINGLE_PLAYER:
            if USED_ALGORITHM == Algorithm.MINIMAX:
                self.game.minimaxPlay(1-self.player, maxDepth=self.maxDepth, evaluate=EVALUATION_FUNCTION, enablePrint=False)
            elif USED_ALGORITHM == Algorithm.RANDOM:
                self.game.randomPlay(1-self.player, enablePrint=False)
            self.history = [self.game.getBoard()]
        
        self.lastX = None
        self.lastY = None
        self.willCapture = False
        self.cnt = 0
        self.btn = [[None]*self.game.size for _ in range(self.game.size)]

        frm_board = tk.Frame(master=window)
        frm_board.pack(fill=tk.BOTH, expand=True)
        for i in range(self.game.size):
            frm_board.columnconfigure(i, weight=1, minsize=IMG_SIZE)
            frm_board.rowconfigure(i, weight=1, minsize=IMG_SIZE)

            for j in range(self.game.size):
                frame = tk.Frame(master=frm_board)
                frame.grid(row=i, column=j, sticky="nsew")

                self.btn[i][j] = tk.Button(master=frame, width=IMG_SIZE, height=IMG_SIZE, relief=tk.FLAT)
                self.btn[i][j].bind("<Button-1>", self.click)
                self.btn[i][j].pack(expand=True, fill=tk.BOTH)
                

        frm_options = tk.Frame(master=window)
        frm_options.pack(expand=True)
        btn_undo = tk.Button(master=frm_options, command=self.undo, text="Undo")
        btn_undo.pack(side=tk.LEFT, padx=5, pady=5)

        btn_redo = tk.Button(master=frm_options, command=self.redo, text="Redo")
        btn_redo.pack(side=tk.LEFT, padx=5, pady=5)

        frm_counter = tk.Frame(master=window)
        frm_counter.pack(expand=True)
        self.lbl_counter = tk.Label(master=frm_counter)
        self.lbl_counter.pack()

        self.update()
        nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
        self.highlight(nextPositions)
        window.mainloop()

    def update(self):
        for i in range(self.game.size):
            f = i % 2 == 1
            for j in range(self.game.size):

                if f:
                    self.btn[i][j]['bg'] = 'gray30'
                else:
                    self.btn[i][j]['bg'] = 'white'
                img = blank_img
                if self.game.board[i][j] == Checkers.BLACK_MAN:
                    img = black_man_img
                elif self.game.board[i][j] == Checkers.BLACK_KING:
                    img = black_king_img
                elif self.game.board[i][j] == Checkers.WHITE_MAN:
                    img = white_man_img
                elif self.game.board[i][j] == Checkers.WHITE_KING:
                    img = white_king_img

                self.btn[i][j]["image"] = img
                
                f = not f
        self.lbl_counter['text'] = f'Moves without capture: {self.cnt}'
        window.update()
    
    def highlight(self, positions: Positions):
        for x in range(self.game.size):
            for y in range(self.game.size):
                defaultbg = self.btn[x][y].cget('bg')
                self.btn[x][y].master.config(highlightbackground=defaultbg, highlightthickness=3)

        for position in positions:
            x, y = position
            self.btn[x][y].master.config(highlightbackground="yellow", highlightthickness=3)

    def click(self, event):
        info = event.widget.master.grid_info()
        x, y = info["row"], info["column"]
        if self.lastX == None or self.lastY == None:
            moves = self.game.nextMoves(self.player)
            found = (x, y) in [move[0] for move in moves]
            
            if found:
                self.lastX = x
                self.lastY = y
                normal, capture = self.game.nextPositions(x, y)
                positions = normal if len(capture) == 0 else capture
                self.highlight(positions)
            else:
                print("Invalid position")
            return

        normalPositions, capturePositions = self.game.nextPositions(self.lastX, self.lastY)
        positions = normalPositions if (len(capturePositions) == 0) else capturePositions
        if (x,y) not in positions:
            print("invalid move")
            if not self.willCapture:
                self.lastX = None
                self.lastY = None
                nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
                self.highlight(nextPositions)
            return

        canCapture, removed, _ = self.game.playMove(self.lastX, self.lastY, x, y)
        self.highlight([])
        self.update()
        self.cnt += 1
        self.lastX = None
        self.lastY = None
        self.willCapture = False

        if removed != 0:
            self.cnt = 0
        if canCapture:
            _, nextCaptures = self.game.nextPositions(x, y)
            if len(nextCaptures) != 0:
                self.willCapture = True
                self.lastX = x
                self.lastY = y
                self.highlight(nextCaptures)
                return

        if GAME_MODE == Mode.SINGLE_PLAYER:
            cont, reset = True, False
            if USED_ALGORITHM == Algorithm.MINIMAX:
                self.maxDepth = difficulty.get()
                if self.maxDepth == 1:
                    print("这是傻瓜模式")
                    cont, reset = self.game.randomPlay(1 - self.player, enablePrint=False)
                else:
                    print("AI开始行动了")
                    evaluate = EVALUATION_FUNCTION
                    # self.maxDepth-1 means maxDepth range from 1 to 4
                    cont, reset = self.game.minimaxPlay(1 - self.player, maxDepth=self.maxDepth-1, evaluate=evaluate,
                                                        enablePrint=False)
            elif USED_ALGORITHM == Algorithm.RANDOM:
                cont, reset = self.game.randomPlay(1-self.player, enablePrint=False)
            self.cnt += 1
            if not cont:
                messagebox.showinfo(message="You Won!", title="Checkers")
                window.destroy()
                return
            self.update()
            if reset:
                self.cnt = 0
        else:
            self.player = 1-self.player

        if self.cnt >= 100:
            messagebox.showinfo(message="Draw!", title="Checkers")
            window.destroy()
            return
        
        nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
        self.highlight(nextPositions)
        if len(nextPositions) == 0:
            if GAME_MODE == Mode.SINGLE_PLAYER:
                messagebox.showinfo(message="You lost!", title="Checkers")
            else:
                winner = "BLACK" if self.player == Checkers.WHITE else "WHITE"
                messagebox.showinfo(message=f"{winner} Player won!", title="Checkers")
            window.destroy()

        self.history = self.history[:self.historyPtr+1]
        self.history.append(self.game.getBoard())
        self.historyPtr += 1

    def undo(self):
        if self.historyPtr > 0 and not self.willCapture:
            self.historyPtr -= 1
            self.game.setBoard(self.history[self.historyPtr])
            self.update()

            self.lastX = self.lastY = None
            nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
            self.highlight(nextPositions)
        else:
            print("Can't undo")
    
    def redo(self):
        if self.historyPtr < len(self.history)-1 and not self.willCapture:
            self.historyPtr += 1
            self.game.setBoard(self.history[self.historyPtr])
            self.update()

            self.lastX = self.lastY = None
            nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
            self.highlight(nextPositions)
        else:
            print("Can't redo")

GUI()