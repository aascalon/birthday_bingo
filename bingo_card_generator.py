import random
import json
import argparse
import pathlib

def fill_list_from_file(filename):
    output_list = []
    with open(filename) as file: 
        for line in file:
            stripped_line = line.rstrip()            
            output_list.append(stripped_line)

    return output_list

def generate_master_dict(input_files): 
    """Takes in an array of text files and generates the master dictionary of possible square contents"""
    master_dict = {}
    for file in input_files: 
        category_name = file.stem
        master_dict.update({category_name: fill_list_from_file(file)})
    
    return master_dict

def generate_bingo_card(master_dict, seed):

    positions =  [
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
    
    # Create the list of questions on the card
    for category, questions in master_dict.items(): 
        selected_questions = random.sample(questions, 3)
        
        for i in range(len(selected_questions)):
            card_list.append((selected_questions[i], category))
    
    random.shuffle(card_list)

    for index, (key, value) in enumerate(card.items()): 
        bingo_square = {"content" : card_list[index][0],
                        "spice_level": card_list[index][1]
                        }
        card[key] = bingo_square

    return card

def generate_unique_bingo_cards(count, master_dict):
    unique_cards = set()
    while len(unique_cards) < count:
        card = generate_bingo_card(master_dict)  # Convert list to tuple for set storage
        unique_cards.add(card)

    return [list(card) for card in unique_cards]

def _parse_args():
    parser = argparse.ArgumentParser(description="Generates a JSON of inquisitive bingo cards")
   
    parser.add_argument(
        'player_count',
        type=int,
        help='Number of bingo cards to generate'
    )

    parser.add_argument(
        '-f',
        '--file',
        type=pathlib.Path,
        default='bingo_cards.json',
        help='Output JSON file path'
    )

    parser.add_argument(
        '-s',
        '--seed',
        type=int,
        default=None,
        help='Seed for generating the cards. Suggestion: use a combination of your birthday and age!'
    )

    parser.add_argument(
        '--questions',
        nargs=3,
        type=pathlib.Path,
        metavar=('file1', 'file2', 'file3'),
        default=['question_bank/innocent.txt','question_bank/mild.txt','question_bank/spicy.txt']
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = _parse_args()

    filename = args.file
    filename.parent.mkdir(parents=True, exist_ok=True)

    game_seed = args.seed
    master_files = args.questions
    
    bingo_cards_dict = {}
    master_dict = generate_master_dict(master_files)
    for i in range(args.player_count):
        bingo_cards_dict.update({i+1 : generate_bingo_card(master_dict, game_seed)}) # one-based indexing
        if game_seed is not None:
            game_seed += i
            random.seed(game_seed)

    
    # Write the full dictionary to JSON
    with open(filename, 'w') as out_file:
        json.dump(bingo_cards_dict, out_file, indent=4)

    print(f"Successfully saved {args.player_count} bingo cards to {filename}.")


