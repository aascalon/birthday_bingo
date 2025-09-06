import random
import json

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
        master_dict.update({file[:-4] : fill_list_from_file(file)})
    
    return master_dict

def generate_bingo_card(master_dict):
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


if __name__ == "__main__":
    filename = 'bingo_cards.json'

    player_count = int(input('How many people are playing?\n'))  # Change this to generate more cards
    master_files = ['innocent.txt',
                    'mild.txt', 
                    'spicy.txt']
    bingo_cards_dict = {}
    master_dict = generate_master_dict(master_files)
    for i in range(player_count):
        bingo_cards_dict.update({i+1 : generate_bingo_card(master_dict)})
    
    # Write the full dictionary to JSON
    with open(filename, 'w') as out_file:
        json.dump(bingo_cards_dict, out_file, indent=4)

    print(f"Successfully saved {player_count} bingo cards to {filename}.")


