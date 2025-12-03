from collections import Counter
from itertools import combinations
import math
import time
import sqlite3 as sql
import numpy as np

# Creating class of cards and deck

ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
suits = ["\u2663", "\u2666", "\u2665", "\u2660"]

class Card:
    values = {"A": 0.91, "2": 0.07, "3": 0.14, "4": 0.21, "5": 0.28, "6": 0.35, "7": 0.42, "8": 0.49, "9": 0.56, "T": 0.63, "J": 0.7, "Q": 0.77, "K": 0.84}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = self.values[self.rank]

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    def __repr__(self):
        return f"{self.rank}{self.suit}"


deck = [Card(rank, suit) for rank in ranks for suit in suits]

# Poker hands

class Poker_Hands:

    def __init__(self, hand_name):
        values = {"Highest_Card": 0, "Pair": 1, "Two_Pairs": 2, "Three_of_a_Kind": 3, "Straight": 4, "Flush": 5, "Full_House": 6, "Four_of_a_Kind": 7, "Straight_Flush": 8, "Royal_Flush": 9}
        self.hand_name = hand_name
        self.hand_value = values[hand_name]

    def __eq__(self, other):
        return isinstance(other, Poker_Hands) and self.hand_name == other.hand_name
    
    def __hash__(self):
        return hash((self.hand_name))


Highest_Card = Poker_Hands("Highest_Card")
Pair = Poker_Hands("Pair")
Two_Pairs = Poker_Hands("Two_Pairs")
Three_of_a_Kind = Poker_Hands("Three_of_a_Kind")
Straight = Poker_Hands("Straight")
Flush = Poker_Hands("Flush")
Full_House = Poker_Hands("Full_House")
Four_of_a_Kind = Poker_Hands("Four_of_a_Kind")
Straight_Flush = Poker_Hands("Straight_Flush")
Royal_Flush = Poker_Hands("Royal_Flush")

class Stage:
    def __init__(self, stage_name, board_unrevealed, board_revealed):
        self.stage_name = stage_name
        self.board_unrevealed = board_unrevealed
        self.board_revealed = board_revealed


Preflop = Stage('preflop', 5, [])
Flop = Stage('flop', 2, [])
Turn = Stage('turn', 1, [])
River = Stage('river', 0, [])


def canonical_form(comb):
    mapping = {}
    next_symbol = ord('A')
    result = []
    for s in comb:
        if s not in mapping:
            mapping[s] = chr(next_symbol)
            next_symbol += 1
        result.append(mapping[s])
    return ''.join(result)


def checking_hand(hand):

    set = Highest_Card
    hand = sorted(hand, key=lambda card: card.value, reverse=True)
    suit = Counter([card.suit for card in hand])
    set_value = hand[0].value + 0.01*hand[1].value + 0.0001*hand[2].value + 0.000001*hand[3].value + 0.00000001*hand[4].value
    rank_counts = Counter([card.rank for card in hand])
    is_flush = len(suit) == 1
    is_straight = len(rank_counts) == 5 and (round(100*hand[0].value) == round(100*hand[-1].value + 28) or (hand[0].rank == "A" and hand[1].rank == "5"))

    # determining poker hand and its value

    if is_flush and is_straight and hand[-1].rank == "T":
        set = Royal_Flush
        set_value = Royal_Flush.hand_value

    elif is_flush and is_straight:
        x = hand[0].value
        if hand[-1].rank == "2":
            x = hand[1].value
        set = Straight_Flush
        set_value = round(Straight_Flush.hand_value + x, 2)

    elif sorted(list(rank_counts.values()), reverse=True) == [4, 1]:
        set = Four_of_a_Kind
        set_value = round(Four_of_a_Kind.hand_value + hand[1].value + 0.005*hand[-1].value + 0.005*hand[0].value, 4)

    elif sorted(list(rank_counts.values()), reverse=True) == [3, 2]:
        set = Full_House
        set_value = round(Full_House.hand_value + hand[2].value + 0.005*hand[0].value + 0.005*hand[-1].value, 4)

    elif is_flush:
        set = Flush
        set_value = round(Flush.hand_value + hand[0].value + 0.01*hand[1].value + 0.0001*hand[2].value + 0.000001*hand[3].value + 0.00000001*hand[4].value, 10)

    elif is_straight:
        x = hand[0].value
        if hand[-1].rank == '2' and hand[0].rank == 'A':
            x = hand[1].value
        set = Straight
        set_value = round(Straight.hand_value + x, 2)

    elif sorted(list(rank_counts.values()), reverse=True)[0] == 3:
        set = Three_of_a_Kind
        set_value = round(Three_of_a_Kind.hand_value + hand[2].value + 0.0025*hand[0].value + 0.0025*hand[1].value + 0.0025*hand[3].value + 0.0025*hand[4].value, 4)

    elif sorted(list(rank_counts.values()), reverse=True) == [2, 2, 1]:
        set = Two_Pairs
        set_value = round(Two_Pairs.hand_value + hand[1].value + 0.01*hand[3].value + 0.00003*hand[0].value + 0.00003*hand[-1].value + 0.00003*hand[2].value, 6)

    elif sorted(list(rank_counts.values()), reverse=True)[0] == 2:
        x = 0
        for i in range(1, 5):
            if hand[i].value == hand[i - 1].value:
                x = hand[i].value
        set = Pair
        set_value = round(Pair.hand_value + x + 0.002*hand[0].value + 0.002*hand[1].value + 0.002*hand[2].value + 0.002*hand[3].value + 0.002*hand[4].value, 4)

    return set, set_value


# Counting number of wins grouped by poker hand, draws and loses

# start_hands as a tuple which elements are lists with two Card objects inside it

def simulating_games_from_given_stage(stage, *start_hands):
    used_cards = [card for hand in start_hands for card in hand[0]]
    game_deck = [i for i in deck if i not in used_cards]
    wins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    overall_sets = [0 for _ in range(10)]
    draws = 0
    loses = 0

    # Creating unique boards for better simulation results
    sets = combinations(game_deck, stage.board_unrevealed)
    suits_order = ['\u2663', '\u2666', '\u2665', '\u2660']
    start = time.perf_counter()
    for board in sets:
        all_hands = {}
        for index, hand in enumerate(start_hands):
            checked_set = sorted(list(hand[0]) + list(board), key=lambda c: (c.value, suits_order.index(c.suit)))

            vals_repr = checked_set[0].rank + checked_set[1].rank + checked_set[2].rank + checked_set[3].rank + checked_set[4].rank + checked_set[5].rank + checked_set[6].rank

            suits = []
            for card in checked_set:
                suits.append(card.suit)

            suits_repr = canonical_form(suits)

            set_name, set_value = start_hands[index][1][(suits_repr, vals_repr)]

            all_hands[index] = (set_name, set_value)

    # Comparing values of starting hands and determining, which hand is a winner (assuming: all_hands[0] is checked, other hands are opponents, so their wins are counted as loses

        winning_value = max(val[1] for val in all_hands.values())
        winning_players = [idx for idx, val in all_hands.items() if val[1] == winning_value]
        
        if 0 not in winning_players:
            loses += 1

        elif len(winning_players) == 1 and winning_players[0] == 0:
            wins[Poker_Hands(all_hands[0][0]).hand_value] += 1

        else:
            draws += 1

        overall_sets[Poker_Hands(all_hands[0][0]).hand_value] += 1

    end = time.perf_counter()
    print(end - start)
    print([el[0] for el in start_hands])
    print(wins + [draws, loses])
    print("Overall: ", overall_sets)
    return wins + [draws, loses]


# Creating dataframe with all texas hold'em outcomes

def creating_all_7_element_combinations_from_poker_deck(deck, sql_driver):

    con = sql_driver.connect("/Users/pi3k4r/Desktop/POKER_analytics/Poker_Database.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS All_Poker_Outcomes(suits_repr CHAR(7), vals_repr CHAR(7), set_name VARCHAR(15), set_value REAL, PRIMARY KEY (suits_repr, vals_repr));""")
    deck = sorted(deck, key= lambda c: c.value)
    deck = [card for card in deck if card.rank in ['2', '4', '3']]
    all_poker_boards = combinations(deck, 7)
    idx = 0
    times = 1
    batch = []
    suits_order = ['\u2663', '\u2666', '\u2665', '\u2660']
    start = time.perf_counter()
    start1 = time.perf_counter()

    for combination in all_poker_boards:
        combination = sorted(combination, key= lambda c: (c.value, suits_order.index(c.suit)))
        suits = []
        for card in combination:
            suits.append(card.suit)

        suits_repr = canonical_form(suits)
        vals_repr = combination[0].rank + combination[1].rank + combination[2].rank + combination[3].rank + combination[4].rank + combination[5].rank + combination[6].rank

        max_set_value = 0
        highest_set = ""

        for hand in combinations(combination, 5):
            check = checking_hand(hand)

            if check[1] > max_set_value:
                max_set_value = check[1]
                highest_set = check[0].hand_name

        batch.append((suits_repr, vals_repr, highest_set, max_set_value))

        if idx == 500000:
            cur.executemany(
                """INSERT OR IGNORE INTO All_Poker_Outcomes(suits_repr, vals_repr, set_name, set_value) VALUES (?, ?, ?, ?)""", batch)
            batch.clear()
            print(idx*times, " W czasie: ", time.perf_counter() - start1)
            con.commit()
            idx = 0
            times += 1
            start1 = time.perf_counter()
        idx += 1
    cur.executemany(
        """INSERT OR IGNORE INTO All_Poker_Outcomes(suits_repr, vals_repr, set_name, set_value) VALUES (?, ?, ?, ?)""", batch)
    con.commit()
    end = time.perf_counter()

    print("Total working time: ", end - start)

# creating_all_7_element_combinations_from_poker_deck(deck, sql)

# deck = sorted(deck, key= lambda c: c.value)
# deck = [card for card in deck if card.rank in ['9', 'T', 'J', 'Q', 'K', 'A']]
# all_poker_boards = combinations(deck, 7)
# con = sql.connect("/Users/pi3k4r/Desktop/POKER_analytics/Poker_Database.db")
# cur = con.cursor()
# all_poker_boards = combinations(deck, 7)
# idx = 0
# times = 1
# batch = []
# suits_order = ['\u2663', '\u2666', '\u2665', '\u2660']
# start = time.perf_counter()
# start1 = time.perf_counter()

# for combination in all_poker_boards:
#     combination = sorted(combination, key= lambda c: (c.value, suits_order.index(c.suit)))
#     suits = []
#     for card in combination:
#         suits.append(card.suit)

#     suits_repr = canonical_form(suits)

#     vals_repr = combination[0].rank + combination[1].rank + combination[2].rank + combination[3].rank + combination[4].rank + combination[5].rank + combination[6].rank

#     max_set_value = 0
#     highest_set = ""

#     for hand in combinations(combination, 5):
#         check = checking_hand(hand)

#         if check[1] > max_set_value:
#             max_set_value = check[1]
#             highest_set = check[0].hand_name

#     batch.append((suits_repr, vals_repr, highest_set, max_set_value))


# cur.executemany(
#     """INSERT OR IGNORE INTO All_Poker_Outcomes(suits_repr, vals_repr, set_name, set_value) VALUES (?, ?, ?, ?)""", batch)
# con.commit()
# end = time.perf_counter()

# print("Total working time: ", end - start)

# con.commit()

# creating_all_7_element_combinations_from_poker_deck(deck, sql)