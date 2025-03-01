import random
import json

SEED = 19980305
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
    card_dict = {}
    card_list = []

    random.seed(SEED) 
    for category, list in master_dict.items(): 
        card_dict.update({category : random.sample(range(len(list)-1), k=3)})

    for spice_level, indices in card_dict.items(): 
        for idx in range(len(indices)): 
            rand_idx = indices[idx]
            indices[idx] = {"content": master_dict[spice_level][rand_idx], 
                            "spice_level" : spice_level 
                            }
            card_list.append(indices[idx])
    random.shuffle(card_list)
    for index, (key, value) in enumerate(card.items()): 
        card[key] = card_list[index]

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
    for i in range(player_count):
        bingo_cards_dict.update({i+1 : None})
    master_dict = generate_master_dict(master_files)
    # bingo_cards = generate_unique_bingo_cards(num_cards, master_dict)
    
    # Store each card with an index in the dictionary
    for i in range(player_count):
        bingo_cards_dict[i+1] = generate_bingo_card(master_dict)
    # Write the full dictionary to JSON
    with open(filename, 'w') as out_file:
        json.dump(bingo_cards_dict, out_file, indent=4)

    print(f"Successfully saved {player_count} bingo cards to {filename}.")


