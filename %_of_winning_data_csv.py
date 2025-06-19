from Poker_Tools import deck, prob_of_win_preflop
from itertools import combinations
import csv
import os

s = "\u2660"
d = "\u2666"
h = "\u2665"
c = "\u2663"

# Calculating for each starting hand (suited and unsuited) overall chances for winning a game
# Creating a .csv files with data of every simulation

dicktionary = {'s': s, 'd': d, 'h': h, 'c': c}

preflop_suited_1 = combinations([card for card in deck if card.suit == s], 2)
preflop_1unsuited1 = [[card1, card2] for card1 in deck if card1.suit == s for card2 in deck if card2.suit == d]
preflop_2unsuited1 = [[card1, card2] for card1 in deck if card1.suit == h for card2 in deck if card2.suit == d]
seen = set()
preflop_1unsuited1sd = []

for card1 in sorted(deck, key = lambda c: c.value):
    if card1.suit != s:
        continue
    for card2 in sorted(deck, key = lambda c: c.value):
        if card2.suit != d:
            continue

        values = tuple(sorted([card1.value, card2.value]))
        if values not in seen:
            seen.add(values)
            preflop_1unsuited1sd.append(sorted([card1, card2], key=lambda c: c.value))

for start_hand1 in preflop_suited_1:
    if os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\Suited_vs_2Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_suited_vs_2unsuited.csv') and os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\Suited_vs_1Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_suited_vs_1unsuited.csv') and os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\Suited_vs_Suited\{start_hand1[0].rank}_{start_hand1[1].rank}_suited_vs_suited_different.csv') and os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\Suited_vs_Suited\{start_hand1[0].rank}_{start_hand1[1].rank}_suited_vs_suited_same.csv'):
        continue
    start_hand1 = list(start_hand1)

    preflop_suited_same2 = combinations([card for card in deck if card.suit == s and card not in start_hand1], 2)
    preflop_suited_different2 = combinations([card for card in deck if card.suit == d], 2)
    preflop_1unsuited2 = [[card1, card2] for card1 in deck if card1.suit == s and card1 not in start_hand1 for card2 in
                          deck if card2.suit == h]
    seen2 = set()
    preflop_2unsuited2 = []

    for card1 in sorted(deck, key = lambda c: c.value):
        if card1.suit != c:
            continue
        for card2 in sorted(deck, key = lambda c: c.value):
            if card2.suit != h:
                continue

            values = tuple(sorted([card1.value, card2.value]))
            if values not in seen2:
                seen2.add(values)
                preflop_2unsuited2.append(sorted([card1, card2], key=lambda c: c.value))

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_suited_same2:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\Suited_vs_Suited\{start_hand1[0].rank}_{start_hand1[1].rank}_suited_vs_suited_same.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_suited_different2:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\Suited_vs_Suited\{start_hand1[0].rank}_{start_hand1[1].rank}_suited_vs_suited_different.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_1unsuited2:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\Suited_vs_1Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_suited_vs_1unsuited.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_2unsuited2:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\Suited_vs_2Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_suited_vs_2unsuited.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)


for start_hand1 in preflop_1unsuited1:
    if os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\1Unsuited_vs_Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_1unsuited_vs_unsuited.csv') and os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\1Unsuited_vs_Suited\{start_hand1[0].rank}_{start_hand1[1].rank}_1unsuited_vs_suited.csv'):
        continue

    preflop_suited2 = combinations([card for card in deck if card.suit == s and card not in start_hand1], 2)
    preflop_unsuited2_different = [[card1, card2] for card1 in deck if card1.suit == s and card1 not in start_hand1 for
                                   card2 in deck if card2.suit == h]

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_suited2:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\1Unsuited_vs_Suited\{start_hand1[0].rank}_{start_hand1[1].rank}_1unsuited_vs_suited.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_unsuited2_different:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\1Unsuited_vs_Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_1unsuited_vs_unsuited.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)

for start_hand1 in preflop_1unsuited1sd:
    if os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\2Unsuited_vs_Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_2unsuited_vs_unsuited_same.csv'):
        continue

    preflop_unsuited2_same = [[card1, card2] for card1 in deck if card1.suit == s and card1 not in start_hand1 for card2
                              in deck if card2.suit == d and card2 not in start_hand1]

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_unsuited2_same:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\2Unsuited_vs_Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_2unsuited_vs_unsuited_same.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)

for start_hand1 in preflop_1unsuited1sd:
    if os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\2Unsuited_vs_Suited\{start_hand1[0].rank}_{start_hand1[1].rank}_2unsuited_vs_suited.csv') and os.path.exists(fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\2Unsuited_vs_Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_2unsuited_vs_unsuited_different.csv'):
        continue
        
    preflop_suited_same2 = combinations([card for card in deck if card.suit == h], 2)
    seen1 = set()
    preflop_2unsuited22 = []

    for card1 in sorted(deck, key = lambda c: c.value):
        if card1.suit != c:
            continue
        for card2 in sorted(deck, key = lambda c: c.value):
            if card2.suit != h:
                continue

            values = tuple(sorted([card1.value, card2.value]))
            if values not in seen1:
                seen1.add(values)
                preflop_2unsuited22.append(sorted([card1, card2], key=lambda c: c.value))

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_suited_same2:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\2Unsuited_vs_Suited\{start_hand1[0].rank}_{start_hand1[1].rank}_2unsuited_vs_suited.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)

    data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins',
             'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws',
             'Loses']]

    for start_hand2 in preflop_2unsuited22:
        start_hand2 = list(start_hand2)
        vs_hand, wins, draws, loses = prob_of_win_preflop(start_hand1, start_hand2, 2175)
        row = [f"{vs_hand[0]}|{vs_hand[1]}"] + wins + [draws, loses]
        data.append(row)

    file_path = fr'C:\Users\Jakub Piekarski\OneDrive\Pulpit\Poker_data\2Unsuited_vs_Unsuited\{start_hand1[0].rank}_{start_hand1[1].rank}_2unsuited_vs_unsuited_different.csv'

    with open(file_path, mode='w', newline='') as file:
        w = csv.writer(file)
        w.writerows(data)
