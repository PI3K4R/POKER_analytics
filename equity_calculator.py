from Poker_Tools import Card, simulating_games_from_preflop_stage
from dwumian_Newtona import dwumian
num_of_players = int(input("How many players?: "))

i = 1
s = "\u2660"
d = "\u2666"
h = "\u2665"
c = "\u2663"
dictionary = {'s': s, 'd': d, 'h': h, 'c': c}
starting_hands = ()

while i <= num_of_players:
    card1_input = tuple(input(f"Player{i} first card (s = \u2660, d = \u2666, h = \u2665, c = \u2663): "))
    if card1_input[0] in ['t', 'j', 'q', 'k', 'a']:
        rank = card1_input[0].upper()
    else:
        rank = card1_input[0]
    suit = dictionary[card1_input[1]]
    card1 = Card(rank, suit)
    card2_input = input(f"Player{i} second card (s = \u2660, d = \u2666, h = \u2665, c = \u2663)(6\u2666): ")
    if card2_input[0] in ['t', 'j', 'q', 'k', 'a']:
        rank = card2_input[0].upper()
    else:
        rank = card2_input[0]
    suit = dictionary[card2_input[1]]
    card2 = Card(rank, suit)
    starting_hands = starting_hands + ([card1, card2],)
    i += 1

sim_number = dwumian(22,5)
print(sim_number)
print(simulating_games_from_preflop_stage(sim_number, *starting_hands))

