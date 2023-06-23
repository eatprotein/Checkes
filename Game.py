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
MAX_DEPTH = 5
EVALUATION_FUNCTION = Checkers.evaluate2
INCREASE_DEPTH = True

# def from_rgb(rgb):
#     """translates an rgb tuple of int to a tkinter friendly color code
#     """
#     r, g, b = rgb
#     return f'#{r:02x}{g:02x}{b:02x}'

class GUI:

    def __init__(self) -> None:
        super().__init__()
        self.game = Checkers(CHECKER_SIZE)
        self.history = [self.game.getBoard()]
        self.historyPtr = 0

        self.maxDepth = MAX_DEPTH

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

        # # Create main canvas
        # self.windowsize = self.game.size * IMG_SIZE
        # self.canvas = tk.Canvas(master=window, width=self.windowsize, height=self.windowsize, bg='WHITE')
        # self.canvas.pack()

        # 建立一个8*8的矩阵用于存储button
        # self.btn = [[None]*self.game.size for _ in range(self.game.size)]

        # frm_board = tk.Frame(master=window)
        # frm_board.pack(fill=tk.BOTH, expand=True)

        self.windowsize = self.game.size * IMG_SIZE
        self.canvas = tk.Canvas(master=window, width=480, height=480, bg='WHITE')
        self.canvas.pack()

        # for i in range(self.game.size):
        #     # frm_board.columnconfigure(i, weight=1, minsize=IMG_SIZE)
        #     # frm_board.rowconfigure(i, weight=1, minsize=IMG_SIZE)
        #
        #     for j in range(self.game.size):
        #         # Create main canvas
        #
        #         # frame = tk.Frame(master=frm_board)
        #         # frame.grid(row=i, column=j, sticky="nsew")
        #
        #         self.btn[i][j] = tk.Button(master=self.canvas, width=IMG_SIZE, height=IMG_SIZE, relief=tk.FLAT)
        #         # self.btn[i][j].bind("<Button-1>", self.click)
        #
        #         self.btn[i][j].bind("<Button-1>", lambda event, row=i, col=j: self.click(event, row, col))
        #         self.canvas.create_window((30+60*j), (30+60*i), anchor='c', window=self.btn[i][j], width=60, height=60)
        #         # self.btn[i][j].place(x=(30 + 61 * j), y=(30 + 61 * i), anchor='c', width=50, height=50)
        #         # self.btn[i][j].pack(expand=True, fill=tk.BOTH)

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

        self.canvas.bind("<Button-1>", self.click)

        # self.draw_board()
        self.update()
        nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
        self.highlight(nextPositions)
        window.mainloop()
        # self.canvas.bind("<Button-1>", handle_click)

    def update(self):
        # 清空画布
        self.canvas.delete("all")

        # 画出棋盘的方格
        for row in range(self.game.size):
            f = row % 2 == 1
            for col in range(self.game.size):
                # 根据行列号计算方格的坐标
                x1 = col * IMG_SIZE
                y1 = row * IMG_SIZE
                x2 = x1 + IMG_SIZE
                y2 = y1 + IMG_SIZE

                if f:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="gray")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")

                if self.game.board[row][col] == Checkers.BLACK_MAN:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
                elif self.game.board[row][col] == Checkers.BLACK_KING:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
                    self.canvas.create_polygon(x1 + 30, y1 + 10, x1 + 20, y1 + 20, x1 + 10, y1 + 10,
                                               x1 + 15, y1 + 30, x1 + 5, y1 + 40, x1 + 30, y1 + 35,
                                               x1 + 55, y1 + 40, x1 + 45, y1 + 30, x1 + 50, y1 + 10,
                                               x1 + 30, y1 + 15, fill="white")
                elif self.game.board[row][col] == Checkers.WHITE_MAN:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")
                elif self.game.board[row][col] == Checkers.WHITE_KING:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")
                    self.canvas.create_polygon(x1 + 30, y1 + 10, x1 + 20, y1 + 20, x1 + 10, y1 + 10,
                                               x1 + 15, y1 + 30, x1 + 5, y1 + 40, x1 + 30, y1 + 35,
                                               x1 + 55, y1 + 40, x1 + 45, y1 + 30, x1 + 50, y1 + 10,
                                               x1 + 30, y1 + 15, fill="black")

                self.canvas.create_text(x1+30, y1+30, text=f'{row},{col}')
                f = not f

        self.lbl_counter['text'] = f'Moves without capture: {self.cnt}'
        window.update()

        nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
        print(nextPositions)

    # def update(self):
    #     for i in range(self.game.size):
    #         f = i % 2 == 1
    #         for j in range(self.game.size):
    #
    #             if f:
    #                 self.btn[i][j]['bg'] = 'gray30'
    #             else:
    #                 self.btn[i][j]['bg'] = 'white'
    #
    #             # img = blank_img
    #             # if self.game.board[i][j] == Checkers.BLACK_MAN:
    #             #     img = black_man_img
    #             # elif self.game.board[i][j] == Checkers.BLACK_KING:
    #             #     img = black_king_img
    #             # elif self.game.board[i][j] == Checkers.WHITE_MAN:
    #             #     img = white_man_img
    #             # elif self.game.board[i][j] == Checkers.WHITE_KING:
    #             #     img = white_king_img
    #             #
    #             # self.btn[i][j]["image"] = img
    #             #
    #
    #             img = ''
    #             if self.game.board[i][j] == Checkers.BLACK_MAN:
    #                 img = 'B'
    #             elif self.game.board[i][j] == Checkers.BLACK_KING:
    #                 img = 'BK'
    #             elif self.game.board[i][j] == Checkers.WHITE_MAN:
    #                 img = 'W'
    #             elif self.game.board[i][j] == Checkers.WHITE_KING:
    #                 img = 'WK'
    #
    #             self.btn[i][j]["text"] = f'{img}({i},{j})'
    #
    #             f = not f
    #     self.lbl_counter['text'] = f'Moves without capture: {self.cnt}'
    #     window.update()
    #
    #     nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
    #     print(nextPositions)


    def highlight(self, positions):
        # for x in range(self.game.size):
        #     for y in range(self.game.size):
        #
        #         # defaultbg = self.btn[x][y].cget('bg')
        #         # self.btn[x][y]["bg"] = defaultbg
        #         #
        #         # # self.btn[x][y].master.config(borderwidth = 2)
        #         # self.btn[x][y].master.config(highlightbackground=defaultbg, highlightthickness=0)

        for position in positions:
            x, y = position
            x1 = y * IMG_SIZE
            y1 = x * IMG_SIZE
            x2 = x1 + IMG_SIZE
            y2 = y1 + IMG_SIZE
            self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="red", width=4)
            # self.btn[x][y]["bg"] = 'yellow'
            # # self.btn[x][y].config(highlightbackground="yellow", highlightthickness=0)

    def click(self, event):

        row = event.x
        col = event.y
        print(row,col)
        x = col // IMG_SIZE
        y = row // IMG_SIZE
        print(x, y)


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
                evaluate = EVALUATION_FUNCTION
                if self.cnt > 20:
                    evaluate = Checkers.endGame
                    if INCREASE_DEPTH:
                        self.maxDepth = 7
                else:
                    evaluate = Checkers.evaluate2
                    self.maxDepth = MAX_DEPTH
                    
                cont, reset = self.game.minimaxPlay(1-self.player, maxDepth=self.maxDepth, evaluate=evaluate, enablePrint=False)
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