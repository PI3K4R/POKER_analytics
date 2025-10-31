from itertools import combinations
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import os
import csv
import sqlite3 as sql
from Poker_Tools import deck, simulating_games_from_given_stage, Preflop
import pandas as pd


def subset_of_db(sql_driver, db_path, *hand_ranks):
    con = sql_driver.connect(db_path)
    cur = con.cursor()

    expression_for_select_operation = ''

    for rank in hand_ranks:
        expression_for_select_operation += f'%{rank}%'

    result = cur.execute(f"""SELECT * FROM All_Poker_Outcomes WHERE vals_repr LIKE \'{expression_for_select_operation}\'
    """)

    subset = {(v, s): (set_name, set_value) for v, s, set_name, set_value in result}
    
    return subset


def generating_poker_csv_for_specified_hand(spc_hand, list_of_opponents, poker_stage, folder, db_path):

    if os.path.exists(fr'\Users\pi3k4r\Desktop\Poker_analytics\{folder}\{spc_hand[0].rank}_{spc_hand[1].rank}'):
        print(fr"File: \Users\pi3k4r\Desktop\Poker_analytics\{folder}\{spc_hand[0].rank}_{spc_hand[1].rank} exists")

    else:
        spc_hand_db = subset_of_db(sql, db_path, spc_hand[0].rank, spc_hand[1].rank)

        data = [['vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins', 'Straight_Wins', 'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins', 'Royal_Flush_Wins', 'Draws', 'Loses']]

        for opponent in list_of_opponents:
            opponent_db = subset_of_db(sql, db_path, opponent[0].rank, opponent[1].rank)
            result = simulating_games_from_given_stage(poker_stage, (spc_hand, spc_hand_db), (opponent, opponent_db))

            data.append([f'{opponent[0].rank}_{opponent[1].rank}'] + result)

        file_path = fr'\Users\pi3k4r\Desktop\Poker_analytics\{folder}\{spc_hand[0].rank}_{spc_hand[1].rank}.csv'

        with open(file_path, mode='w', newline='') as file:
            w = csv.writer(file)
            w.writerows(data)

        file.close()

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

    preflop_suited_same2 = combinations([card for card in deck if card.suit == s and card not in start_hand1], 2)
    preflop_suited_different2 = combinations([card for card in deck if card.suit == d], 2)
    preflop_1unsuited2 = [[card1, card2] for card1 in deck if card1.suit == s and card1 not in start_hand1 for card2 in deck if card2.suit == h]
    seen2 = set()
    preflop_2unsuited2 = []

    generating_poker_csv_for_specified_hand(start_hand1, preflop_suited_same2, Preflop, 'Suited_vs_Suited_same', fr'/Users/pi3k4r/Desktop/Poker_analytics/Poker_Database.db')

    generating_poker_csv_for_specified_hand(start_hand1, preflop_suited_different2, Preflop, 'Suited_vs_Suited_different')

    generating_poker_csv_for_specified_hand(start_hand1, preflop_1unsuited2, Preflop, 'Suited_vs_1Unsuited_')

    generating_poker_csv_for_specified_hand(start_hand1, preflop_2unsuited2, Preflop, 'Suited_vs_2Unsuited')


for start_hand1 in preflop_1unsuited1:

    preflop_suited2 = combinations([card for card in deck if card.suit == s and card not in start_hand1], 2)
    preflop_unsuited2_different = [[card1, card2] for card1 in deck if card1.suit == s and card1 not in start_hand1 for card2 in deck if card2.suit == h]

    generating_poker_csv_for_specified_hand(start_hand1, preflop_suited2, Preflop, '1Unsuited_vs_Suited')

    generating_poker_csv_for_specified_hand(start_hand1, preflop_unsuited2_different, Preflop, '1Unsuited_vs_Unsuited')


for start_hand1 in preflop_1unsuited1sd:

    preflop_unsuited2_same = [[card1, card2] for card1 in deck if card1.suit == s and card1 not in start_hand1 for card2 in deck if card2.suit == d and card2 not in start_hand1]
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

    generating_poker_csv_for_specified_hand(start_hand1, preflop_unsuited2_same, Preflop, '2Unsuited_vs_Unsuited_same')

    generating_poker_csv_for_specified_hand(start_hand1, preflop_suited_same2, Preflop, '2Unsuited_vs_Suited')

    generating_poker_csv_for_specified_hand(start_hand1, preflop_2unsuited22, Preflop, '2Unsuited_vs_Unsuited_different')
