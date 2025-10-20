from collections import Counter
from itertools import combinations
import math
import time
import sqlite3 as sql

# Creating class of cards and deck


ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
suits = ["\u2663", "\u2666", "\u2665", "\u2660"]

class Card:
    values = {"A": 0.91, "2": 0.07, "3": 0.14, "4": 0.21, "5": 0.28, "6": 0.35, "7": 0.42, "8": 0.49, "9": 0.56,
              "T": 0.63, "J": 0.7, "Q": 0.77, "K": 0.84}

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

    def __init__(self, hand_name, hand_value):
        self.hand_name = hand_name
        self.hand_value = hand_value


Highest_Card = Poker_Hands("Highest_Card", 0)
Pair = Poker_Hands("Pair", 1)
Two_Pairs = Poker_Hands("Two_Pairs", 2)
Three_of_a_Kind = Poker_Hands("Three_of_a_Kind", 3)
Straight = Poker_Hands("Straight", 4)
Flush = Poker_Hands("Flush", 5)
Full_House = Poker_Hands("Full_House", 6)
Four_of_a_Kind = Poker_Hands("Four_of_a_Kind", 7)
Straight_Flush = Poker_Hands("Straight_Flush", 8)
Royal_Flush = Poker_Hands("Royal_Flush", 9)

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
    set_value = (hand[0].value + 0.01*hand[1].value + 0.0001*hand[2].value + 0.000001*hand[3].value +
                 0.00000001*hand[4].value)
    rank_counts = Counter([card.rank for card in hand])
    is_flush = len(suit) == 1
    is_straight = len(rank_counts) == 5 and (hand[0].value == hand[-1].value + 0.28 or
                                             (hand[0].rank == "A" and hand[1].rank == "5"))

    # determining poker hand and its value

    if is_flush and is_straight and hand[-1].rank == "T":
        set = Royal_Flush
        set_value = Royal_Flush.hand_value

    elif is_flush and is_straight:
        x = hand[0].value
        if hand[-1].rank == "2":
            x = hand[1].value
        set = Straight_Flush
        set_value = Straight_Flush.hand_value + x

    elif sorted(list(rank_counts.values()), reverse=True) == [4, 1]:
        set = Four_of_a_Kind
        set_value = Four_of_a_Kind.hand_value + hand[1].value + 0.005*hand[-1].value + 0.005*hand[0].value

    elif sorted(list(rank_counts.values()), reverse=True) == [3, 2]:
        set = Full_House
        set_value = Full_House.hand_value + hand[2].value + 0.005*hand[0].value + 0.005*hand[-1].value

    elif is_flush:
        set = Flush
        set_value = (Flush.hand_value + hand[0].value + hand[1].value*0.01 + hand[2].value*0.0001 +
                     hand[3].value*0.000001 + hand[4].value*0.00000001)

    elif is_straight:
        x = hand[0].value
        if hand[-1].rank == '2':
            x = hand[1].value
        set = Straight
        set_value = Straight.hand_value + x

    elif sorted(list(rank_counts.values()), reverse=True)[0] == 3:
        set = Three_of_a_Kind
        set_value = Three_of_a_Kind.hand_value + hand[2].value

    elif sorted(list(rank_counts.values()), reverse=True)[0] == 2 and sorted(rank_counts.values(),
                                                                             reverse=True)[1] == 2:
        set = Two_Pairs
        set_value = (Two_Pairs.hand_value + hand[1].value + hand[3].value*0.01 + 0.00003*hand[0].value +
                     0.00003*hand[-1].value + 0.00003*hand[2].value)

    elif sorted(list(rank_counts.values()), reverse=True)[0] == 2:
        x = 0
        for i in range(1, 5):
            if hand[i].value == hand[i - 1].value:
                x = hand[i].value
        set = Pair
        set_value = Pair.hand_value + x

    return set, set_value


# Counting number of wins grouped by poker hand, draws and loses

# start_hands as a tuple which elements are lists with two Card objects inside it

def simulating_games_from_preflop_stage(stage, *start_hands):
    used_cards = [card for hand in start_hands for card in hand]
    game_deck = [i for i in deck if i not in used_cards]
    wins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    draws = 0
    loses = 0

    # Creating unique boards for better simulation results
    sets = combinations(game_deck, stage.board)

    for board in sets:
        all_hands = {}
        # Counting values for each given hand + chosen board
        for index, hand in enumerate(start_hands):
            checked_set = list(combinations(list(hand) + list(board), 5))
            highest_set = "Highest_Card"
            starting_hand_value = (sorted(hand, key=lambda card: card.value, reverse=True)[0].value +
                                    0.01*sorted(hand, key=lambda card: card.value, reverse=True)[1].value)
            max_set_value = starting_hand_value

            for x in checked_set:
                check = checking_hand(x)

                if check[1] > max_set_value:
                    max_set_value = check[1]
                    highest_set = check[0].hand_name

            all_hands[index] = (highest_set, max_set_value, starting_hand_value)

    # Comparing values of starting hands and determining, which hand is a winner (assuming: all_hands[0] is checked, other hands are opponents, so their wins are counted as loses for main hand

        winning_value = max(val[1] for val in all_hands.values())
        winning_set = [val[0] for val in all_hands.values() if val[1] == winning_value]
        winning_starting_hand = max(val[2] for val in all_hands.values())
        winning_players_at_start = [idx for idx, val in all_hands.items() if val[2] == winning_starting_hand]
        winning_players = [idx for idx, val in all_hands.items() if val[1] == winning_value]

        if '0' not in [str(player) for player in winning_players]:
            loses += 1

        elif len(winning_players) == 1 and winning_players[0] == 0:
            wins[math.floor(winning_value)] += 1

        elif '0' in [str(player) for player in winning_players_at_start] and len(winning_players_at_start) == 1 and winning_set not in ("Two_Pairs", "Four_of_a_Kind", "Highest_Card"):
            wins[math.floor(winning_value)] += 1

        elif '0' not in [str(player) for player in winning_players_at_start] and winning_set not in ("Two_Pairs", "Four_of_a_Kind", "Highest_Card"):
            loses += 1

        else:
            draws += 1



    return wins + [draws, loses]


# Creating dataframe with all texas hold'em outcomes

def creating_all_7_element_combinations_from_poker_deck(deck, sql_driver):

    con = sql_driver.connect("Poker_Database.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS All_Poker_Outcomes(suits_repr CHAR(7), vals_repr CHAR(14), set_name VARCHAR(15), set_value REAL, PRIMARY KEY (suits_repr, vals_repr));""")
    all_poker_boards = combinations(deck, 7)
    suit_code = {"\u2660": 's', "\u2666": 'd', "\u2665": 'h', "\u2663": 'c'}
    idx = 0
    times = 1
    batch = []
    start = time.perf_counter()
    start1 = time.perf_counter()

    for combination in all_poker_boards:
        board = sorted(combination, key=lambda card: card.value)
        suits = []
        for card in board:
            suits.append(card.suit)

        suits_repr = canonical_form(suits)

        vals = board[0].value + board[1].value * 0.01 + board[2].value * 0.0001 + board[3].value * 0.000001 + board[
            4].value * 0.00000001 + board[5].value * 0.0000000001 + board[6].value * 0.000000000001

        vals_repr = str(vals)[2:16]

        max_set_value = 0
        highest_set = "Highest_Card"

        for hand in combinations(board, 5):
            check = checking_hand(hand)

            if check[1] > max_set_value:
                max_set_value = check[1]
                highest_set = check[0].hand_name

        set_name = highest_set
        set_value = max_set_value

        batch.append((suits_repr, vals_repr, set_name, set_value))

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

    con.commit()
    end = time.perf_counter()

    print("Total working time: ", end - start)
