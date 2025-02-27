import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os

class BingoScorer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Adrianna's Bingo Scorer!")
        self.geometry("1000x1000")
        self.configure(padx=0, pady=0)
        
        # Define spice level to point mapping
        self.level_points = {
            "innocent": 1,
            "mild": 2,
            "spicy": 5
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
        
        # Create frames
        self.create_header_frame()
        self.create_results_frame()

        self.create_grid_frame()
        self.create_controls_frame()
        
        # Initialize the grid
        self.initialize_grid()
        
        # Load cards data
        self.load_cards_data()
    # def create_window_grid()
        
    def create_header_frame(self):
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="Custom Bingo Scorer", font=("Arial", 16, "bold"))
        title_label.pack()
        
        instructions = "Load a card by ID and mark completed/doubled squares"
        instructions_label = tk.Label(header_frame, text=instructions, font=("Arial", 10))
        instructions_label.pack()
        
        # Add card ID section
        card_frame = tk.Frame(header_frame)
        card_frame.pack(fill="x", pady=10)
        
        tk.Label(card_frame, text="Current Card:").pack(side="left")
        self.card_id_label = tk.Label(card_frame, text="None", width=10)
        self.card_id_label.pack(side="left", padx=5)
        
        load_card_btn = tk.Button(card_frame, text="Load Card by ID", command=self.prompt_card_id)
        load_card_btn.pack(side="left", padx=5)
        
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
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(fill="both", expand=True, pady=5)
        
        # Bingo grid will be added in initialize_grid method

    def create_controls_frame(self):
        controls_frame = tk.Frame(self)
        controls_frame.pack(fill="x", pady=0)
        
        reset_btn = tk.Button(controls_frame, text="Reset Completions", command=self.reset_completions)
        reset_btn.pack(side="left", padx=5)
        
        calc_btn = tk.Button(controls_frame, text="Calculate Score", command=self.calculate_score)
        calc_btn.pack(side="left", padx=5)
        
        save_btn = tk.Button(controls_frame, text="Save Completions", command=self.save_completions)
        save_btn.pack(side="left", padx=5)
        
        load_btn = tk.Button(controls_frame, text="Load Completions", command=self.load_completions)
        load_btn.pack(side="left", padx=5)

    def create_results_frame(self):
        self.results_frame = tk.Frame(self)
        
        self.results_frame.pack(fill="y", pady=0, side=tk.RIGHT)
        
        self.score_label = tk.Label(self.results_frame, text="Score: 0", font=("Arial", 14, "bold"))
        self.score_label.pack(pady=2, side=tk.TOP)
        
        self.details_text = tk.Text(self.results_frame, height=20, width=60)
        self.details_text.pack(fill="x", expand=False)

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
                    
                    # Content text
                    content_frame = tk.Frame(square_frame)
                    content_frame.pack(fill="both", expand=True, padx=5, pady=1)
                    
                    content_text = tk.Text(content_frame, height=3, width=20, wrap="word", font=('Comic Sans MS', 12))
                    content_text.pack(fill="both", expand=True)
                    content_text.config(state="disabled")
                    
                    # Scrollbar for content
                    # scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=content_text.yview)
                    # scrollbar.pack(side="right", fill="y")
                    # content_text.configure(yscrollcommand=scrollbar.set)
                    
                    # Completed checkbox
                    completed_var = tk.BooleanVar(value=False)
                    completed_cb = tk.Checkbutton(square_frame, text="Completed", variable=completed_var,)
                    completed_cb.pack(anchor="nw", padx=0, pady=(0,0),ipady=0)
                    
                    # Doubled checkbox
                    doubled_var = tk.BooleanVar(value=False)
                    doubled_cb = tk.Checkbutton(square_frame, text="New Friend Bonus", variable=doubled_var)
                    doubled_cb.pack(anchor="nw", padx=0, pady=(0,0))
                    
                    # Square info
                    self.squares[position] = {
                        "position_label": position_label,
                        "spice_value": spice_value,
                        "content_text": content_text,
                        "completed_var": completed_var,
                        "doubled_var": doubled_var,
                        "spice_level": None  # Will be set when loading card
                    }
        
        # Configure grid weights
        for i in range(3):
            bingo_frame.grid_columnconfigure(i, weight=1, uniform="col")
            bingo_frame.grid_rowconfigure(i, weight=1, uniform="row")

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
            square["completed_var"].set(False)
            square["doubled_var"].set(False)
        
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
            completed = square["completed_var"].get()
            doubled = square["doubled_var"].get()
            
            if completed and spice_level:
                square_points = self.level_points.get(spice_level, 0)
                if doubled:
                    square_points *= 2
                    doubled_count += 1 
                    if doubled_count >= 5:
                        new_friend_bonus = True
                
                total_score += square_points
                position_text = position.replace("_", " ").title()
                details.append(f"{position_text}: {spice_level.capitalize()} ({self.level_points.get(spice_level, 0)} pts)" + 
                              (f" x2 = {square_points}" if doubled else f" = {square_points}"))
                details.append(f"New friends made: {doubled_count}")
                details.append(f"Running score so far: {total_score}")
        
        self.details_text.delete(1.0, tk.END)
        if details:
            self.details_text.insert(tk.END, f"Scoring Details for Card {self.current_card_id}:\n\n")
            for detail in details:
                self.details_text.insert(tk.END, detail + "\n")
            if new_friend_bonus:
                    total_score *= 2
                    self.details_text.insert(tk.END, 'Entire scorecard multiplied by 2 (New Friend Bonus). Wow!')
            self.details_text.insert(tk.END, f"\nTotal Score: {total_score}")
        else:
            self.details_text.insert(tk.END, "No squares completed yet.")

        self.score_label.config(text=f"Score: {total_score}")

    def load_cards_data(self):
        cards_file = "bingo_cards.json"
        
        if not os.path.exists(cards_file):
            messagebox.showwarning("Warning", f"Cards file '{cards_file}' not found. Please create this file with your bingo card data.")
            return
        
        try:
            with open(cards_file, "r") as f:
                self.cards_data = json.load(f)
            messagebox.showinfo("Success", f"Loaded {len(self.cards_data)} cards from {cards_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cards data: {str(e)}")

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
                spice_level = data.get("spice_level", "")
                square["spice_level"] = spice_level
                square["spice_value"].config(text=spice_level.capitalize(), bg=self.get_color_for_spice_level(spice_level))
                
                # Update content
                content = data.get("content", "")
                square["content_text"].config(state="normal")
                square["content_text"].delete(1.0, tk.END)
                square["content_text"].insert(tk.END, content)
                square["content_text"].config(state="disabled")
        
        messagebox.showinfo("Success", f"Loaded card {card_id}")

    def save_completions(self):
        if not self.current_card_id:
            messagebox.showinfo("Info", "Please load a card first.")
            return
            
        completions = {
            "card_id": self.current_card_id,
            "level_points": self.level_points,
            "squares": {}
        }
        
        for position, square in self.squares.items():
            completions["squares"][position] = {
                "completed": square["completed_var"].get(),
                "doubled": square["doubled_var"].get()
            }
        
        filename = f"completions_{self.current_card_id}.json"
        try:
            with open(filename, "w") as f:
                json.dump(completions, f, indent=2)
            messagebox.showinfo("Success", f"Completions saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save completions: {str(e)}")

    def load_completions(self):
        if not self.current_card_id:
            messagebox.showinfo("Info", "Please load a card first.")
            return
            
        filename = f"completions_{self.current_card_id}.json"
        if not os.path.exists(filename):
            messagebox.showinfo("Info", f"No saved completions found for card {self.current_card_id}.")
            return
            
        try:
            with open(filename, "r") as f:
                completions = json.load(f)
            
            # Update level points
            for level, points in completions["level_points"].items():
                if level in self.level_points:
                    self.level_points[level] = points
            
            # Update level point entries
            points_frame = self.header_frame.winfo_children()[-1]
            for i, level in enumerate(["innocent", "mild", "spicy"]):
                entry = points_frame.winfo_children()[i*2+2]
                entry.delete(0, tk.END)
                entry.insert(0, str(self.level_points[level]))
            
            # Update square completions
            for position, data in completions["squares"].items():
                if position in self.squares:
                    square = self.squares[position]
                    square["completed_var"].set(data.get("completed", False))
                    square["doubled_var"].set(data.get("doubled", False))
            
            messagebox.showinfo("Success", f"Loaded completions for card {self.current_card_id}")
            self.calculate_score()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load completions: {str(e)}")

if __name__ == "__main__":
    app = BingoScorer()
    app.mainloop()