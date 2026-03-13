import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import json
import os
import csv
import argparse
from pathlib import Path

POSITIONS_ORDER = [
    'top_left', 'top_middle', 'top_right',
    'middle_left', 'centre', 'middle_right',
    'bottom_left', 'bottom_middle', 'bottom_right'
]
CSV_COLUMNS = ['id', 'player'] + POSITIONS_ORDER + ['score', 'submit_order']
STATE_TO_CSV = {0: 'INC', 1: 'C', 2: 'C-NF'}

class BingoScorer(tk.Tk):
    def __init__(self, initial_file=None):
        super().__init__()
        
        self.title("Adrianna's Bingo Scorer!")
        self.geometry("1000x1000")
        self.configure(padx=0, pady=0)
        
        # Define spice level to point mapping
        self.level_points = {
            "innocent": 1,
            "mild": 2,
            "spicy": 3
        }
        
        # Position mapping - converts grid positions to position names in JSON
        self.position_mapping = {
            (0, 0): "top_left",
            (0, 1): "top_middle",
            (0, 2): "top_right",
            (1, 0): "middle_left",
            (1, 1): "centre",
            (1, 2): "middle_right",
            (2, 0): "bottom_left",
            (2, 1): "bottom_middle",
            (2, 2): "bottom_right"
        }
        
        # Reverse mapping for loading
        self.reverse_position_mapping = {v: k for k, v in self.position_mapping.items()}
        
        # Store loaded cards data
        self.cards_data = {}
        self.current_card_id = None
        self.cards_file = None
        
        # Create notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.score_tab = tk.Frame(self.notebook)
        self.leaderboard_tab = tk.Frame(self.notebook)
        self.notebook.add(self.score_tab, text="Score Calculation")
        self.notebook.add(self.leaderboard_tab, text="Leaderboard")

        # Create frames
        self.create_header_frame()
        self.create_results_frame()

        self.create_grid_frame()
        self.create_controls_frame()
        self.create_leaderboard_tab()
        
        # Initialize the grid
        self.initialize_grid()

        # Auto-load file if provided
        if initial_file:
            self.cards_file = initial_file
            self.cards_file_label.config(text=initial_file, fg="black")
            self.load_cards_data()
            self.load_card_by_id("1")
    # def create_window_grid()
        
    def create_header_frame(self):
        header_frame = tk.Frame(self.score_tab)
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="Custom Bingo Scorer", font=("Arial", 16, "bold"))
        title_label.pack()
        
        instructions = "Load a card by ID and mark completed/doubled squares"
        instructions_label = tk.Label(header_frame, text=instructions, font=("Arial", 10))
        instructions_label.pack()
        
        # Add JSON file selection
        file_frame = tk.Frame(header_frame)
        file_frame.pack(fill="x", pady=(5, 0))

        tk.Label(file_frame, text="Cards JSON:").pack(side="left")
        self.cards_file_label = tk.Label(file_frame, text="No file selected", fg="grey", anchor="w")
        self.cards_file_label.pack(side="left", padx=5, fill="x", expand=True)
        browse_btn = tk.Button(file_frame, text="Browse...", command=self.browse_cards_file)
        browse_btn.pack(side="left", padx=5)

        # Add card ID section
        card_frame = tk.Frame(header_frame)
        card_frame.pack(fill="x", pady=10)
        
        tk.Label(card_frame, text="Card ID:").pack(side="left")
        self.card_id_entry = tk.Entry(card_frame, width=6)
        self.card_id_entry.pack(side="left", padx=5)
        self.card_id_entry.bind("<Return>", lambda e: self.load_card_from_entry())

        load_card_btn = tk.Button(card_frame, text="Load", command=self.load_card_from_entry)
        load_card_btn.pack(side="left", padx=5)

        tk.Label(card_frame, text="Current:").pack(side="left", padx=(10, 0))
        self.card_id_label = tk.Label(card_frame, text="None", width=6)
        self.card_id_label.pack(side="left", padx=5)

        refresh_data_btn = tk.Button(card_frame, text="Refresh Cards Data", command=self.load_cards_data)
        refresh_data_btn.pack(side="left", padx=5)
        
        # Add point values display
        points_frame = tk.Frame(header_frame)
        points_frame.pack(fill="x", pady=0)
        
        tk.Label(points_frame, text="Points per spice level:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        
        for i, level in enumerate(["innocent", "mild", "spicy"]):
            tk.Label(points_frame, text=f"{level.capitalize()}:").grid(row=0, column=i*2+1, padx=(10, 0))
            level_entry = tk.Entry(points_frame, width=2)
            level_entry.insert(0, str(self.level_points[level]))
            level_entry.grid(row=0, column=i*2+2, padx=(0, 10))
            level_entry.bind("<KeyRelease>", lambda event, lvl=level, entry=level_entry: self.update_level_points(lvl, entry))

    def create_grid_frame(self):
        self.grid_frame = tk.Frame(self.score_tab)
        self.grid_frame.pack(fill="both", expand=True, pady=5)
        
        # Bingo grid will be added in initialize_grid method

    def create_controls_frame(self):
        controls_frame = tk.Frame(self.score_tab)
        controls_frame.pack(fill="x", pady=0)
        
        reset_btn = tk.Button(controls_frame, text="Reset Completions", command=self.reset_completions)
        reset_btn.pack(side="left", padx=5)

    def create_results_frame(self):
        self.results_frame = tk.Frame(self.score_tab)

        self.results_frame.pack(fill="y", pady=0, side=tk.RIGHT)
        
        self.score_label = tk.Label(self.results_frame, text="Score: 0", font=("Arial", 48, "bold"))
        self.score_label.pack(pady=2, side=tk.TOP)

        self.details_text = tk.Text(self.results_frame, height=20, width=60)
        self.details_text.pack(fill="x", expand=False)

        calc_btn = tk.Button(self.results_frame, text="Calculate Score", command=self.calculate_score,
                             font=("Arial", 16, "bold"), padx=20, pady=10)
        calc_btn.pack(pady=5)

        self.submit_order_label = tk.Label(self.results_frame, text="Next submit order: —", font=("Arial", 11))
        self.submit_order_label.pack(pady=(10, 2))

        player_frame = tk.Frame(self.results_frame)
        player_frame.pack(pady=(5, 0))
        tk.Label(player_frame, text="Player name:", font=("Arial", 11)).pack(side="left")
        self.player_entry = tk.Entry(player_frame, width=20, font=("Arial", 11))
        self.player_entry.pack(side="left", padx=5)

        submit_btn = tk.Button(self.results_frame, text="Submit", command=self.submit_card,
                               font=("Arial", 16, "bold"), padx=20, pady=10, bg="#4CAF50", fg="white")
        submit_btn.pack(pady=5)

    def initialize_grid(self):
        # Clear existing widgets in grid_frame
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Create bingo grid frame
        bingo_frame = tk.Frame(self.grid_frame)
        bingo_frame.pack(fill="both", expand=True)
        # Grid setup
        self.squares = {}
        for row in range(3):
            for col in range(3):
                position = self.position_mapping.get((row, col))
                if position:
                    square_frame = tk.Frame(bingo_frame, relief="raised", borderwidth=2)
                    square_frame.grid(row=row, column=col, padx=5, pady=0, sticky="nsew")
       
                    # Position label
                    position_label = tk.Label(square_frame, text=position.replace("_", " ").title(), font=("Arial", 12, "bold"))
                    position_label.pack(anchor="nw", padx=5, pady=(5, 0))
                    
                    # Spice level display with colorful label
                    spice_frame = tk.Frame(square_frame)
                    spice_frame.pack(fill="x", pady=2)
                    
                    spice_label = tk.Label(spice_frame, text="Level:", font=("Arial", 9))
                    spice_label.pack(side="left", padx=5)
                    
                    spice_value = tk.Label(spice_frame, text="Unknown", width=8, relief="ridge", 
                                          bg="white", font=("Arial", 9, "bold"))
                    spice_value.pack(side="left", padx=5)
                    
                    # Content label
                    content_text = tk.Label(square_frame, text="", wraplength=220,
                                            font=('Comic Sans MS', 12), justify="left", anchor="nw")
                    content_text.pack(fill="both", expand=True, padx=5, pady=1)
                    content_text.bind("<Configure>", lambda e: e.widget.config(wraplength=e.width))
                    
                    # Scrollbar for content
                    # scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=content_text.yview)
                    # scrollbar.pack(side="right", fill="y")
                    # content_text.configure(yscrollcommand=scrollbar.set)
                    
                    # State indicator label
                    state_label = tk.Label(square_frame, text="", font=("Arial", 9, "bold"), justify="center")
                    state_label.pack(anchor="center", pady=(2, 4))

                    # Square info
                    self.squares[position] = {
                        "frame": square_frame,
                        "position_label": position_label,
                        "spice_value": spice_value,
                        "content_text": content_text,
                        "state_label": state_label,
                        "state": 0,  # 0=incomplete, 1=complete, 2=complete+bonus
                        "spice_level": None  # Will be set when loading card
                    }
                    self._bind_click(square_frame, position)
        
        # Configure grid weights
        for i in range(3):
            bingo_frame.grid_columnconfigure(i, weight=1, uniform="col")
            bingo_frame.grid_rowconfigure(i, weight=1, uniform="row")

    def _color_for_state(self, state):
        return {0: "#F0F0F0", 1: "#FFD700", 2: "#90EE90"}[state]

    def _text_for_state(self, state):
        return {0: "", 1: "Complete", 2: "Complete\n+ New Friend Bonus"}[state]

    def _set_frame_color(self, widget, color):
        try:
            widget.config(bg=color)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._set_frame_color(child, color)

    def _bind_click(self, widget, position):
        widget.bind("<Button-1>", lambda e, p=position: self.cycle_square_state(p))
        for child in widget.winfo_children():
            self._bind_click(child, position)

    def cycle_square_state(self, position):
        square = self.squares[position]
        square["state"] = (square["state"] + 1) % 3
        state = square["state"]
        self._set_frame_color(square["frame"], self._color_for_state(state))
        square["state_label"].config(text=self._text_for_state(state))

    def update_level_points(self, level, entry):
        try:
            value = int(entry.get())
            if value < 0:
                value = 0
                entry.delete(0, tk.END)
                entry.insert(0, "0")
            self.level_points[level] = value
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, str(self.level_points[level]))

    def reset_completions(self):
        for position, square in self.squares.items():
            square["state"] = 0
            self._set_frame_color(square["frame"], self._color_for_state(0))
            square["state_label"].config(text="")

        self.score_label.config(text="Score: 0")
        self.details_text.delete(1.0, tk.END)

    def get_color_for_spice_level(self, spice_level):
        if spice_level == "innocent":
            return "#E8F5E9"  # Light green
        elif spice_level == "mild":
            return "#FFF8E1"  # Light yellow
        elif spice_level == "spicy":
            return "#FFEBEE"  # Light red
        return "white"

    def calculate_score(self):
        if not self.current_card_id:
            messagebox.showinfo("Info", "Please load a card first.")
            return
            
        total_score = 0
        details = []
        doubled_count = 0
        new_friend_bonus = False
        for position, square in self.squares.items():
            spice_level = square["spice_level"]
            state = square["state"]

            if state > 0 and spice_level:
                square_points = self.level_points.get(spice_level, 0)
                if state == 2:
                    square_points += 2
                    doubled_count += 1
                    if doubled_count >= 6:
                        new_friend_bonus = True

                total_score += square_points
                position_text = position.replace("_", " ").title()
                details.append(f"{position_text}: {spice_level.capitalize()} ({self.level_points.get(spice_level, 0)} pts)" +
                              (f" +2 = {square_points}" if state == 2 else f" = {square_points}"))
                details.append(f"New friends made: {doubled_count}")
                details.append(f"Running score so far: {total_score}")
        
        self.details_text.delete(1.0, tk.END)
        if details:
            self.details_text.insert(tk.END, f"Scoring Details for Card {self.current_card_id}:\n\n")
            for detail in details:
                self.details_text.insert(tk.END, detail + "\n")
            if new_friend_bonus:
                    total_score = int(total_score * 1.5)
                    self.details_text.insert(tk.END, 'Entire scorecard multiplied by 1.5x (New Friend Bonus). Wow!')
            self.details_text.insert(tk.END, f"\nTotal Score: {total_score}")
        else:
            self.details_text.insert(tk.END, "No squares completed yet.")

        self.score_label.config(text=f"Score: {total_score}")
        return total_score

    def browse_cards_file(self):
        path = filedialog.askopenfilename(
            title="Select bingo cards JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.cards_file = path
            self.cards_file_label.config(text=path, fg="black")
            self.load_cards_data()

    def load_cards_data(self):
        if not self.cards_file:
            messagebox.showinfo("Info", "Please select a cards JSON file first.")
            return

        if not os.path.exists(self.cards_file):
            messagebox.showwarning("Warning", f"Cards file '{self.cards_file}' not found.")
            return

        try:
            with open(self.cards_file, "r") as f:
                self.cards_data = json.load(f)
            messagebox.showinfo("Success", f"Loaded {len(self.cards_data)} cards from {self.cards_file}")
            self.update_submit_order_display()
            self.update_leaderboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cards data: {str(e)}")

    def load_card_from_entry(self):
        card_id = self.card_id_entry.get().strip()
        if card_id:
            self.load_card_by_id(card_id)

    def prompt_card_id(self):
        if not self.cards_data:
            messagebox.showinfo("Info", "Please load cards data first.")
            return
            
        card_ids = list(self.cards_data.keys())
        card_id = simpledialog.askstring("Load Card", "Enter Card ID:", parent=self)
        if card_id:
            self.load_card_by_id(card_id)

    def load_card_by_id(self, card_id):
        if card_id not in self.cards_data:
            messagebox.showerror("Error", f"Card ID {card_id} not found in loaded cards data.")
            return
            
        card_data = self.cards_data[card_id]
        
        # Update current card ID
        self.current_card_id = card_id
        self.card_id_label.config(text=card_id)
        
        # Reset completions
        self.reset_completions()
        
        # Update grid with card data
        for position, data in card_data.items():
            if position in self.squares:
                square = self.squares[position]
                
                # Update spice level
                spice_level = data.get("category", "")
                square["spice_level"] = spice_level
                square["spice_value"].config(text=spice_level.capitalize(), bg=self.get_color_for_spice_level(spice_level))
                
                # Update content
                content = data.get("content", "")
                square["content_text"].config(text=content)
        
        messagebox.showinfo("Success", f"Loaded card {card_id}")

    def create_leaderboard_tab(self):
        tk.Label(self.leaderboard_tab, text="Leaderboard", font=("Arial", 20, "bold")).pack(pady=10)

        columns = ('rank', 'player', 'score', 'submit_order', 'card_id')
        self.leaderboard_tree = ttk.Treeview(self.leaderboard_tab, columns=columns, show='headings')

        self.leaderboard_tree.heading('rank', text='Rank')
        self.leaderboard_tree.heading('player', text='Player')
        self.leaderboard_tree.heading('score', text='Score')
        self.leaderboard_tree.heading('submit_order', text='Submit Order')
        self.leaderboard_tree.heading('card_id', text='Card ID')

        self.leaderboard_tree.column('rank', width=60, anchor='center')
        self.leaderboard_tree.column('player', width=200)
        self.leaderboard_tree.column('score', width=80, anchor='center')
        self.leaderboard_tree.column('submit_order', width=120, anchor='center')
        self.leaderboard_tree.column('card_id', width=80, anchor='center')

        self.leaderboard_tree.pack(fill="both", expand=True, padx=10, pady=5)

    def update_leaderboard(self):
        csv_path = self.get_csv_path()
        if not csv_path or not os.path.exists(csv_path):
            return

        with open(csv_path, 'r', newline='') as f:
            rows = list(csv.DictReader(f))

        rows.sort(key=lambda r: (-int(r['score']), int(r['submit_order'])))

        for item in self.leaderboard_tree.get_children():
            self.leaderboard_tree.delete(item)

        for rank, row in enumerate(rows, 1):
            self.leaderboard_tree.insert('', 'end', values=(
                rank,
                row.get('player', ''),
                row['score'],
                row['submit_order'],
                row['id'],
            ))

    def get_csv_path(self):
        if self.cards_file:
            return str(Path(self.cards_file).with_suffix('.csv'))
        return None

    def update_submit_order_display(self):
        csv_path = self.get_csv_path()
        if not csv_path:
            self.submit_order_label.config(text="Next submit order: —")
            return
        count = 0
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='') as f:
                count = sum(1 for row in csv.DictReader(f))
        self.submit_order_label.config(text=f"Next submit order: {count + 1}")

    def submit_card(self):
        if not self.current_card_id:
            messagebox.showinfo("Info", "Please load a card first.")
            return

        csv_path = self.get_csv_path()
        if not csv_path:
            messagebox.showinfo("Info", "Please load a cards JSON file first.")
            return

        if not self.player_entry.get().strip():
            messagebox.showwarning("Missing name", "Please enter the player's name before submitting.")
            return

        score = self.calculate_score()
        if score is None:
            return

        # Load existing rows
        existing_rows = []
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='') as f:
                existing_rows = list(csv.DictReader(f))

        # Check for duplicate
        existing_index = None
        existing_submit_order = None
        for i, row in enumerate(existing_rows):
            if row['id'] == str(self.current_card_id):
                existing_index = i
                existing_submit_order = row['submit_order']
                break

        if existing_index is not None:
            overwrite = messagebox.askyesno(
                "Card already recorded",
                f"Card ID #{self.current_card_id} is already recorded. Do you want to overwrite the existing entry?"
            )
            if not overwrite:
                return
            submit_order = existing_submit_order
        else:
            submit_order = len(existing_rows) + 1

        # Build new row
        new_row = {'id': str(self.current_card_id), 'player': self.player_entry.get().strip()}
        for pos in POSITIONS_ORDER:
            new_row[pos] = STATE_TO_CSV[self.squares[pos]['state']]
        new_row['score'] = str(score)
        new_row['submit_order'] = str(submit_order)

        if existing_index is not None:
            existing_rows[existing_index] = new_row
        else:
            existing_rows.append(new_row)

        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(existing_rows)

        messagebox.showinfo("Submitted", f"Card {self.current_card_id} saved (submit order: {submit_order}).")
        self.update_submit_order_display()
        self.update_leaderboard()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bingo card scorer")
    parser.add_argument("file", nargs="?", default=None, help="Path to bingo cards JSON file")
    args = parser.parse_args()

    app = BingoScorer(initial_file=args.file)
    app.mainloop()