"""
Bingo Card Generator

This script generates custom bingo cards from text files containing prompts of different "spice levels".

SETUP:
------
1. Create text files with your bingo prompts:
   - innocent.txt: Safe/family-friendly prompts
   - mild.txt: Moderately spicy prompts  
   - spicy.txt: Bold/risqué prompts

2. Each text file should have one prompt per line
   - Empty lines and whitespace-only lines will be ignored
   - Each card will randomly select 3 prompts from each category (9 total per card)

USAGE:
------
Basic usage (interactive):
    python bingo_generator.py

With command line arguments:
    python bingo_generator.py --player-count 5
    python bingo_generator.py --maximize-unique
    python bingo_generator.py --player-count 8 --maximize-unique

ARGUMENTS:
----------
--player-count N        Number of bingo cards to generate
--maximize-unique       Ensure maximum unique prompts across all cards
                       (no prompt reuse until all unique prompts are used)

OUTPUT:
-------
Creates 'bingo_cards.json' containing all generated cards with:
- Each card numbered (1, 2, 3, etc.)
- 9 positions per card (top_left, top_middle, etc.)
- Each square contains: prompt content and spice level

EXAMPLE FILES:
--------------
innocent.txt:
    Laughed at a funny meme
    Helped a neighbor
    Found a good parking spot

mild.txt:
    Sent a risky text
    Stayed up past midnight
    Ate dessert for breakfast

spicy.txt:
    Had an awkward encounter with an ex
    Told a white lie to avoid plans
    Stalked someone on social media
"""

import random
import json
import argparse

def fill_list_from_file(filename):
    output_list = []
    with open(filename) as file: 
        for line in file:
            stripped_line = line.strip()  # Use strip() to remove all whitespace
            if stripped_line:  # Only add non-empty strings
                output_list.append(stripped_line)
    return output_list

def generate_master_dict(input_files): 
    """Takes in an array of text files and generates the master dictionary of possible square contents"""
    master_dict = {}
    for file in input_files: 
        master_dict.update({file[:-4] : fill_list_from_file(file)})
    
    return master_dict

def generate_bingo_card(master_dict, used_prompts=None):
    """Generate a bingo card, optionally tracking used prompts for uniqueness"""
    if used_prompts is None:
        used_prompts = set()
    
    positions = [
        'top_left',
        'top_middle', 
        'top_right',
        'middle_left',
        'centre',
        'middle_right',
        'bottom_left',
        'bottom_middle',
        'bottom_right',
    ]
    
    card = dict.fromkeys(positions)
    card_list = []
    
    # Get available prompts for each category
    for category, prompts_list in master_dict.items():
        # Filter out already used prompts if tracking uniqueness
        available_prompts = [p for p in prompts_list if p not in used_prompts] if used_prompts else prompts_list
        
        # If we don't have enough available prompts, use all remaining ones
        num_to_select = min(3, len(available_prompts))
        if num_to_select == 0:
            # If no available prompts, fall back to original list
            available_prompts = prompts_list
            num_to_select = min(3, len(available_prompts))
        
        # Sample from available prompts
        selected_indices = random.sample(range(len(available_prompts)), k=num_to_select)
        
        for idx in selected_indices:
            selected_prompt = available_prompts[idx]
            card_entry = {
                "content": selected_prompt,
                "spice_level": category
            }
            card_list.append(card_entry)
            
            # Track this prompt as used
            if used_prompts is not None:
                used_prompts.add(selected_prompt)
    
    # Shuffle and assign to positions
    random.shuffle(card_list)
    for index, (key, value) in enumerate(card.items()):
        if index < len(card_list):
            card[key] = card_list[index]
        else:
            # Fill remaining positions with None if we run out of prompts
            card[key] = None
    
    return card

def generate_unique_bingo_cards(count, master_dict, maximize_unique_prompts=False):
    """Generate multiple bingo cards, optionally maximizing unique prompts across all cards"""
    cards = []
    used_prompts = set() if maximize_unique_prompts else None
    
    for i in range(count):
        card = generate_bingo_card(master_dict, used_prompts)
        cards.append(card)
    
    return cards

def count_total_available_prompts(master_dict):
    """Count total number of unique non-empty prompts available"""
    return sum(len(prompts) for prompts in master_dict.values())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate bingo cards from text files')
    parser.add_argument('--maximize-unique', action='store_true', 
                       help='Ensure maximum unique prompts across all cards (no duplicates until necessary)')
    parser.add_argument('--player-count', type=int, 
                       help='Number of players (will prompt if not provided)')
    
    args = parser.parse_args()
    
    filename = 'bingo_cards.json'
    
    # Get player count
    if args.player_count:
        player_count = args.player_count
    else:
        player_count = int(input('How many people are playing?\n'))
    
    master_files = ['innocent.txt', 'mild.txt', 'spicy.txt']
    master_dict = generate_master_dict(master_files)
    
    # Check if we have enough unique prompts
    total_prompts = count_total_available_prompts(master_dict)
    prompts_needed = player_count * 9  # 9 squares per card
    
    if args.maximize_unique and prompts_needed > total_prompts:
        print(f"Warning: You need {prompts_needed} prompts for {player_count} unique cards, "
              f"but only {total_prompts} unique prompts are available.")
        print("Some prompts will be reused across cards.")
    
    # Generate cards
    if args.maximize_unique:
        cards_list = generate_unique_bingo_cards(player_count, master_dict, maximize_unique_prompts=True)
        bingo_cards_dict = {i+1: cards_list[i] for i in range(player_count)}
    else:
        bingo_cards_dict = {}
        for i in range(player_count):
            bingo_cards_dict[i+1] = generate_bingo_card(master_dict)
    
    # Write to JSON
    with open(filename, 'w') as out_file:
        json.dump(bingo_cards_dict, indent=4, fp=out_file)
    
    print(f"Successfully saved {player_count} bingo cards to {filename}.")
    if args.maximize_unique:
        print("Cards generated with maximum unique prompts across all players.")
    
    # Print statistics
    used_prompts = set()
    for card in bingo_cards_dict.values():
        for position, square in card.items():
            if square and square.get('content'):
                used_prompts.add(square['content'])
    
    print(f"Total unique prompts used: {len(used_prompts)} out of {total_prompts} available.")