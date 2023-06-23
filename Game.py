import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from Checkers import Checkers
from enum import Enum
import time

window = tk.Tk()
window.title("Checkers")

IMG_SIZE = 60

difficulty = tk.IntVar()
message = tk.StringVar()


class Mode(Enum):
    SINGLE_PLAYER = 0
    MULTIPLE_PLAYER = 1
class Algorithm(Enum):
    MINIMAX = 0
    RANDOM = 1

CHECKER_SIZE = 8
GAME_MODE = Mode.SINGLE_PLAYER
# GAME_MODE = Mode.MULTIPLE_PLAYER
STARTING_PLAYER = Checkers.BLACK
USED_ALGORITHM = Algorithm.MINIMAX
EVALUATION_FUNCTION = Checkers.evaluate2

class GUI:

    def __init__(self):
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


        self.windowsize = self.game.size * IMG_SIZE
        self.canvas = tk.Canvas(master=window, width=480, height=480, bg='WHITE')
        self.canvas.pack()
        #
        frm_options = tk.Frame(master=window)
        frm_options.pack(expand=True)
        btn_undo = tk.Button(master=frm_options, command=self.undo, text="Undo")
        btn_undo.pack(side=tk.LEFT, padx=5, pady=5)
        #
        btn_redo = tk.Button(master=frm_options, command=self.redo, text="Redo")
        btn_redo.pack(side=tk.LEFT, padx=5, pady=5)

        frm_counter = tk.Frame(master=window)
        frm_counter.pack(expand=True)
        self.lbl_counter = tk.Label(master=frm_counter)
        self.lbl_counter.pack()

        # 菜单栏
        menu_bar = tk.Menu(window)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Rule", command=lambda: self.show_rules())
        menu_bar.add_cascade(label="Help", menu=file_menu)
        window.config(menu=menu_bar)

        # 建立button
        btn_rules = tk.Button(master=frm_options, command=lambda: self.show_rules(), text="Rules")
        btn_rules.pack(side=tk.LEFT, padx=5, pady=5)

        self.canvas.bind("<Button-1>", self.click)
        self.update()
        nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
        self.highlight(nextPositions)
        window.mainloop()

    def show_rules(self):
        popup_window = tk.Toplevel()
        popup_window.title("Rules")

        # 添加弹出窗口的内容
        label1 = tk.Label(popup_window, text="Rules for Checkers")
        label2 = tk.Label(popup_window, text="""
        1. Board and pieces:
        - A standard 8×8 board is used.
        - Each player starts with 12 pieces, with one side white and the other black.
        2. Movement rules:
        - Regular white pieces can only move upwards, and regular black pieces can only move downwards.
        - Pieces can only move along the diagonal to adjacent spaces.
        3. Jumping rules:
        - When a piece jumps over an opponent's piece on an adjacent square, the piece that was jumped over is removed.
        - Skipping is mandatory, and players must take advantage of skipping opportunities. That is, if the current 
        player's piece can continue to jump over the opponent's piece during the jumping process, then the player must 
        continue to jump until there are no more jumping opportunities available.
        4. King promotion rule:
        - When a normal piece reaches the last row of the opponent's board (i.e. the opponent's baseline), that piece 
        is promoted to "King".
        - When a normal piece captures an opponent's king, it is crowned "king".
        - A king moves in the same way as a normal piece, but it can move forward and backward in any direction, and 
        has greater flexibility and jumping ability.
        5. Victory conditions:
        - If one player's pieces cannot move further or are eaten by the other player, the game ends.
        - If neither player is able to meet the win condition, the game is declared a draw.
        """, anchor='w',justify='left')
        label1.pack()
        label2.pack()

        # 设置弹出窗口的大小
        popup_window.geometry("750x450")

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
                i = IMG_SIZE/10
                crown = (x1 + 2*i, y1 + 4*i, x1 + 4*i, y1 + 5*i, x1 + 5*i, y1 + 3*i,
                                               x1 + 6*i, y1 + 5*i, x1 + 8*i, y1 + 4*i, x1 + 8*i, y1 + 5*i,
                                               x1 + 7*i, y1 + 7*i, x1 + 3*i, y1 + 7*i, x1 + 2*i, y1 + 5*i)

                triangle = (x1+5*i,y1+2*i, x1+2*i, y1+7*i, x1+8*i, y1+7*i)

                if f:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="gray")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")

                if self.game.board[row][col] == Checkers.BLACK_MAN:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
                    print(x1 + 5, y1 + 5, x2 - 5, y2 - 5)
                elif self.game.board[row][col] == Checkers.BLACK_KING:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
                    # self.canvas.create_polygon(x1 + 30, y1 + 10, x1 + 20, y1 + 20, x1 + 10, y1 + 10,
                    #                            x1 + 15, y1 + 30, x1 + 5, y1 + 40, x1 + 30, y1 + 35,
                    #                            x1 + 55, y1 + 40, x1 + 45, y1 + 30, x1 + 50, y1 + 10,
                    #                            x1 + 30, y1 + 15, fill="white")
                    self.canvas.create_polygon(triangle, fill="white")
                elif self.game.board[row][col] == Checkers.WHITE_MAN:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")
                elif self.game.board[row][col] == Checkers.WHITE_KING:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")
                    # self.canvas.create_polygon(x1 + 30, y1 + 10, x1 + 20, y1 + 20, x1 + 10, y1 + 10,
                    #                            x1 + 15, y1 + 30, x1 + 5, y1 + 40, x1 + 30, y1 + 35,
                    #                            x1 + 55, y1 + 40, x1 + 45, y1 + 30, x1 + 50, y1 + 10,
                    #                            x1 + 30, y1 + 15, fill="black")
                    self.canvas.create_polygon(crown, fill="black")

                self.canvas.create_text(x1+30, y1+30, text=f'{row},{col}')
                f = not f

        # self.lbl_counter['text'] = f'Moves without capture: {self.cnt}'
        window.update()

        nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
        print(nextPositions)

    def highlight(self, positions):
        # for x in range(self.game.size):
        #     for y in range(self.game.size):
        #
        #         # defaultbg = self.btn[x][y].cget('bg')
        #         # self.btn[x][y]["bg"] = defaultbg
        #         #
        #         # # self.btn[x][y].master.config(borderwidth = 2)
        #         # self.btn[x][y].master.config(highlightbackground=defaultbg, highlightthickness=0)
        self.canvas.delete('highlight')
        for position in positions:
            x, y = position
            x1 = y * IMG_SIZE
            y1 = x * IMG_SIZE
            x2 = x1 + IMG_SIZE
            y2 = y1 + IMG_SIZE
            self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="red", width=4, tags='highlight')
            # self.btn[x][y]["bg"] = 'yellow'
            # # self.btn[x][y].config(highlightbackground="yellow", highlightthickness=0)

    def show_message(self, title, message):
        messagebox.showinfo(f"{title}", f"{message}")

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
                self.show_message('warning',"Invalid position!")
            return

        normalPositions, capturePositions = self.game.nextPositions(self.lastX, self.lastY)
        positions = normalPositions if (len(capturePositions) == 0) else capturePositions
        if (x,y) not in positions:
            self.show_message('warning',"Invalid move!")
            if not self.willCapture:
                self.lastX = None
                self.lastY = None
                nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
                self.highlight(nextPositions)
            return

        canCapture, removed, promoted= self.game.playMove(self.lastX, self.lastY, x, y)

        # canCapture, removed, _ = self.game.playMove(self.lastX, self.lastY, x, y)
        self.highlight([])
        time.sleep(0.3)
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
                    while type(reset) is list:
                        time.sleep(0.5)
                        self.update()
                        time.sleep(0.5)
                        cont, reset = self.game.minimaxPlay(1 - self.player, reset,
                                                            evaluate=evaluate,
                                                            enablePrint=False)
                        self.update()

            elif USED_ALGORITHM == Algorithm.RANDOM:
                cont, reset = self.game.randomPlay(1-self.player, enablePrint=False)
            self.cnt += 1
            if not cont:
                messagebox.showinfo(message="You Won!", title="Checkers")
                window.destroy()
                return
            time.sleep(0.6)
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