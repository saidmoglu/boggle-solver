import tkinter as tk
from UI import BoggleDisplay
from Trie import Trie
from Board import *

def get_list_value(lst, index, default=None):
    try:
        return lst[index]
    except IndexError:
        return default

class BoggleGame:
    def __init__(self, init_board):
        self.values = {
        'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
        'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
        'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10,
        '.': 0, '': 0
        }
        self.words_definitions = self.read_words()
        self.words = self.words_definitions.keys()
        self.max_word_len = max(self.words, key=len)
        self.trie = self.build_trie()
        self.board = init_board
        self.words_paths_scores = self.solver()
        self.words_paths_scores.sort(key=lambda content : content[2], reverse=True)

        # Begin UI Part
        self.root = tk.Tk()
        self.root.title("Boggle Solver")
        self.root.geometry("800x600+300+300")

        self.boggle_display = BoggleDisplay(self.root, self.board, self.words_paths_scores, self.word_click_func, self.solve_button_func)
        self.boggle_display.pack(expand=True, fill=tk.BOTH)
        self.boggle_display.display_UI()

        self.root.mainloop()

    def update_display(self):
        self.words_paths_scores = self.solver()
        self.words_paths_scores.sort(key=lambda content : content[2], reverse=True)
        self.boggle_display.update_board(self.board, self.words_paths_scores)

    def solve_button_func(self):
        self.board = self.boggle_display.boggle_board.get_updated_board()
        self.update_display()

    def word_click_func(self, word_coords):
        # Convert the board to columns for easier processing
        columns = list(zip(*self.board))
        coords_set = set(word_coords)
        
        new_columns = []
        
        new_coords_set = {}
        
        new_coords_set = coords_set.union({y 
                                            for coord in coords_set 
                                            for y in {(coord[0],coord[1]+1),
                                                        (coord[0],coord[1]-1),
                                                        (coord[0]+1,coord[1]),
                                                        (coord[0]-1,coord[1])} 
                                            if len(coords_set) > 4 or get_list_value(get_list_value(self.board,y[0],[]),y[1],'') == '#'})

        for col_index, col in enumerate(columns):
            new_col = [letter for row_index, letter in enumerate(col) if (row_index, col_index) not in new_coords_set]
            new_col = [''] * (len(col) - len(new_col)) + new_col + ['']
            new_columns.append(new_col)

        self.board = [list(tup) for tup in zip(*new_columns)]
        while all(v.char == '' for v in self.board[0]):
            self.board.pop(0)
            
        self.update_display()
     
    def read_words(self):
        with open('words.txt') as f:
            lines = f.readlines()
            words_definitions = {key: value for key, value in (item.split("\t", 1) for item in lines[2:])}
            return words_definitions

    def build_trie(self):
        trie = Trie()
        for word in self.words:
            trie.insert(word)
        return trie

    def solver(self):
        rows, cols = len(self.board), len(self.board[0])
        result = []

        def dfs(row, col, path: str, path_coord):
            if not (0 <= row < rows) or not (0 <= col < cols) or (not self.board[row][col].char.isalpha()) or len(path) == self.max_word_len:
                return

            char = self.board[row][col].char
            path += char
            path_coord.append((row,col))

            if not self.trie.start_with(path):
                return

            if self.trie.search(path) and len(path)>2:
                multiplier = 1
                for coord in path_coord:
                    if(self.board[coord[0]][coord[1]].is_yellow):
                        multiplier = multiplier * 2
                score = len(path) * sum(self.values[l] for l in path) * multiplier # incorrect
                result.append((path,path_coord, score))

            temp, self.board[row][col] = self.board[row][col], BoardCell("*") # mark as used

            for i, j in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                dfs(row+i, col+j, path, path_coord.copy())

            self.board[row][col] = temp
            return

        for i in range(rows):
            for j in range(cols):
                dfs(i, j, "", [])

        self.words_paths_scores = result
        return result

# enter each column. Uppercase for yellow squares. black squares are #
vertical_init_board = """
iuzttcl
asl
n
h
s
eym
uiC
oheyw
drsdirp
""".strip()
vertical_init_board = vertical_init_board.split('\n')
max_height = max([len(s) for s in vertical_init_board])
vertical_init_board = [[''] * (max_height - len(s)) + list(s) for s in vertical_init_board ]
init_board = [list(tup) for tup in zip(*vertical_init_board)]
init_board = [[BoardCell(s,True) if s.isupper() else BoardCell(s.upper()) for s in row] for row in init_board]

boggle_game = BoggleGame(init_board)