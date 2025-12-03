import Poker_Tools as PT
from itertools import combinations
from math import floor, ceil
import numpy as np
import time
from random import sample

wins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
overall_sets = [0 for _ in range(10)]
draws = 0
loses = 0

hand1 = [PT.Card('6', '\u2663'), PT.Card('4', '\u2663')]
hand2 = [PT.Card('2', '\u2663'), PT.Card('3', '\u2663')]
deck = [card for card in PT.deck if card not in hand1 and card not in hand2]
boards = combinations(deck, 5)
idx = 0
start = time.perf_counter()
for combination in boards:
    poker_set1 = hand1 + list(combination)
    poker_set2 = hand2 + list(combination)
    max_set_value1 = 0
    max_set_value2 = 0
    max_set_name1 = ''
    max_set_name2 = ''
    for hand in combinations(poker_set1, 5):
        set_name1, set_value1 = PT.checking_hand(hand)
        if set_value1 > max_set_value1:
            max_set_value1 = set_value1
            max_set_name1 = set_name1.hand_name
    overall_sets[PT.Poker_Hands(max_set_name1).hand_value] += 1

    for hand in combinations(poker_set2, 5):
        set_name2, set_value2 = PT.checking_hand(hand)
        if set_value2 > max_set_value2:
            max_set_value2 = set_value2
            max_set_name2 = set_name2.hand_name

    if max_set_value1 > max_set_value2:
        wins[PT.Poker_Hands(max_set_name1).hand_value] += 1

    elif max_set_value1 < max_set_value2:
        loses += 1

    else:
        draws += 1
    
end = time.perf_counter()
print(wins + [draws, loses], '\n', "Czas wykonania: ", end - start)
print(overall_sets)


# print(set_val_calc(Highest_Card.hand_value, 10, 11))

# start1 = time.perf_counter()
# y = 10**10*(1 + 2) + 10**6*(3 + 4 +5)
# end1 = time.perf_counter()
# print((end1 - start1))

# start2 = time.perf_counter()
# x = 10**8*13 + 10**6*15 + 10**4*11+ 10**2*9 + 10*7
# end2 = time.perf_counter()

# print((end2 - start2))