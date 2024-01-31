import tkinter as tk

class WordLabel(tk.Label):
    def __init__(self, master, word_hover_func, word_coords, word_click_func, **kwargs):
        super().__init__(master, **kwargs)
        self.word_hover_func = word_hover_func
        self.word_coords = word_coords
        self.word_click_func = word_click_func
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>",self.word_click_inner_func)

    def on_enter(self, event):
        for x,y in self.word_coords:
            self.word_hover_func((x,y),True)

    def on_leave(self, event):
        for x,y in self.word_coords:
            self.word_hover_func((x,y),False)
    
    def word_click_inner_func(self, event):
        self.word_click_func(self.word_coords)

class WordList(tk.Frame):
    def __init__(self, master, words_paths_scores, word_click_func, word_hover_func, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.words_paths_scores = words_paths_scores
        self.word_hover_func = word_hover_func
        self.word_click_func = word_click_func

        self.canvas = tk.Canvas(self, bg='white')
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        self.inner_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.word_labels = []

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta), "units")

    def display_word_list(self):
        #delete existing
        for word_label in self.word_labels:
            word_label.destroy()
        self.word_labels = []

        row, col = 0, 0
        words_per_row = 3 
        for i, content in enumerate(self.words_paths_scores):
            word, path, score = content
            word_label = WordLabel(self.inner_frame, self.word_hover_func, path, self.word_click_func, text=f"{word} ({score})".format())
            word_label.grid(row=row, column=col, pady=2, padx=5)
            self.word_labels.append(word_label)
            col += 1
            if col >= words_per_row:
                col = 0 
                row += 1 

    def update_scroll_region(self, event):
        """Update the scrolling region every time the size of the inner frame changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class BoggleBoard(tk.Frame):
    def __init__(self,master,board, **kwargs):
        super().__init__(master, **kwargs)
        self.board = board
        self.cells = []
        
    def display_board(self):
        # delete existing
        for row in self.cells:
            for cell in row:
                cell.destroy()

        self.cells = []

        for i in range(len(self.board)):
            row = []
            for j in range(len(self.board[i])):
                entry_var = tk.StringVar()
                def to_uppercase(*args, value=entry_var):
                    current_value = value.get()
                    if current_value:
                        last_char = current_value[-1].upper()
                        value.set(last_char)
                entry_var.trace_add("write", to_uppercase)
                entry_cell = tk.Entry(self,width=2, font=('Arial', 24), justify='center', borderwidth=1,relief="solid", bg='white', textvariable=entry_var)
                entry_cell.insert(0, self.board[i][j].char)
                if(self.board[i][j].is_yellow):
                    entry_cell.config(bg='yellow')
                entry_cell.grid(row=i, column=j, padx=1,pady=1)
                row.append(entry_cell)
            self.cells.append(row)
    
    def get_updated_board(self):
        return [[cell.get() for cell in row] for row in self.cells]

    def highlight_cell(self, coords, highlight=True):
        if highlight:
            if self.cells[coords[0]][coords[1]].cget('bg') == 'white':
                self.cells[coords[0]][coords[1]].config(bg='indianred1')
            elif self.cells[coords[0]][coords[1]].cget('bg') == 'yellow':
                self.cells[coords[0]][coords[1]].config(bg='orange')
        else:
            if self.cells[coords[0]][coords[1]].cget('bg') == 'indianred1':
                self.cells[coords[0]][coords[1]].config(bg='white')
            elif self.cells[coords[0]][coords[1]].cget('bg') == 'orange':
                self.cells[coords[0]][coords[1]].config(bg='yellow')

class BoggleDisplay(tk.Frame):
    def __init__(self, master, board, words_paths, word_click_func, solve_func, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=True) 
        self.grid_rowconfigure(0, weight=1)  
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1)
        
        self.board = board
        self.words_paths = words_paths
        self.boggle_board = BoggleBoard(self, board)
        self.boggle_board.grid(row=0, column=0, sticky="w")

        self.word_list = WordList(self, words_paths, word_click_func, self.boggle_board.highlight_cell)
        self.word_list.grid(row=0, column=1, sticky="nsew")

        self.solve_button = tk.Button(self, text="Solve", command=solve_func)
        self.solve_button.grid(row=len(self.board) + 1, columnspan=len(self.board[0]), pady=10) 


    def display_UI(self):
        self.boggle_board.display_board()
        self.word_list.display_word_list()
    
    def update_board(self, new_board, new_words_paths):
        self.board = new_board
        self.boggle_board.board = new_board
        self.boggle_board.display_board()

        self.word_list.words_paths_scores = new_words_paths
        self.word_list.display_word_list()