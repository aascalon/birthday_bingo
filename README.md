# Adrianna's Birthday Bingo! 
For my 27th birthday I decided to play a variation on icebreaker-style bingo, a favourite of corporate parties and awkward gatherings everywhere. I wanted everyone's bingo card to be unique, with a range of questions ranging from the innocent to the intimately "spicy"🌶️🌶️🌶️. I also wanted different friend groups to interact with one another, as I have attended too many ostensibly social events where attendees simply stuck to the people they knew. 

## Rules
These rules are provided for context since I tailored the code to them. 

### The cards
- Each card has nine squares with a prompt that follows the phrase, "Find someone who...". For example:
    - "worked in the service industry"
    - "has been ejected from an establishment"
- Each square was categorised into one of three tiers: 
    1. Innocent, worth one point. The sort of thing you can ask your grandma. 
    2. Mild, worth two points. Slowly getting into interesting territory.
    3. Spicy, worth five points. Intimate/bold/risqué, perfect for asking strangers! 
- Hence, there were three squares per category on each card.
- Each square also had a checkbox with the words, "Different sticker?" next to it. More on that in the next section.

### The players
- When arriving at the party, each player was given a nametag to fill in and a coloured sticker. 
- Sticker colours were assigned based on social circle, i.e., based on how they knew me. 

### The game
- The game functioned msotly like classic icebreaker bingo, where for each square on their card, players had to find someone who fit that description, and have them sign the square (worth a certain number of points). 
- To encourage inter-group mixing, the **square's points were doubled** if signed by someone wearing a different coloured sticker to the card's owner (i.e., if they weren't in the same social circle). To record this, the "different sticker" checkbox was ticked.
- Signing more than one square on a card was prohibited. 
- If a card had more than 5 signatures from differently-stickered players (i.e., more than half your card was signed by people you didn't already know), **the overall card score was doubled.**
- At the end of the game period I tallied up everyone's points and handed out prizes to the top 3 scorers! 🥇🥈🥉

## Workflow
Refer to each Python script for more detailed instructions, but in summary: 
1. `bingo_card_generator.py` creates a set of randomised bingo cards, whose squares sourced from the files in the question bank. This will output a JSON containing every card (see `bingo_cards.json` as an example).
2. EITHER: 
    - Run `bingo_card_pdf_generator.py` with the JSON as an input. However, this script does not support the points system described above.
    - Develop your own custom solution to generate a set of bingo cards from the JSON (more effort but you can implement any custom scoring this way)

If you're not using my scoring system, you are done! Enjoy your party! 🎉 If not:

3. At the end of the game, run `bingo_card_scoring.py` (a GUI application). It looks for `bingo_cards.json` and loads it. From there, you can load cards by their ID and score them. Of course, if your mental maths is fast you can skip this step entirely, but by this point in the night I was already a few drinks deep and didn't particularly feel up to the challenge.


# Acknowledgements
**My partner**, who designed the bingo card template for my birthday, as well as developing the pipeline (not currently on GitHub) to ingest the JSON contents and turn them into actual printable cards. 

**Lulu Liu** who gave this repo a test drive for her birthday, and in doing so, implemented the uniqueness optimiser and PDF generator! 