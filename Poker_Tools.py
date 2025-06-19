from collections import Counter
from random import sample
from itertools import combinations
import math


suits = ["\u2663", "\u2666", "\u2665", "\u2660"]
ranks = [ "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]


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

def checking_hand(hand):

    set = Highest_Card
    hand = sorted(hand, key= lambda card: card.value, reverse= True)
    suit = Counter([card.suit for card in hand])
    set_value = hand[0].value + 0.01*hand[1].value + 0.0001*hand[2].value + 0.000001*hand[3].value + 0.00000001*hand[4].value
    rank_counts = Counter([card.rank for card in hand])
    is_flush = len(suit) == 1
    is_straight = len(rank_counts) == 5 and (hand[0].value == hand[-1].value + 0.28 or (hand[0].rank == "A" and hand[1].rank == "5" and hand[2].rank == "4" and hand[3].rank == "3" and hand[4].rank == "2"))

    if is_flush and is_straight and hand[-1].rank == "T":
        set = Royal_Flush
        set_value = Royal_Flush.hand_value

    elif is_flush and is_straight:
        x = hand[0].value
        if hand[-1].rank == "2":
            x = hand[1].value
        set = Straight_Flush
        set_value = Straight_Flush.hand_value + x


    elif sorted(list(rank_counts.values()), reverse= True) == [4,1]:
        set = Four_of_a_Kind
        set_value = Four_of_a_Kind.hand_value + hand[1].value + 0.005*hand[-1].value + 0.005*hand[0].value

    elif sorted(list(rank_counts.values()), reverse= True) == [3,2]:
        set = Full_House
        set_value = Full_House.hand_value + hand[2].value + 0.005*hand[0].value + 0.005*hand[-1].value

    elif is_flush:
        set = Flush
        set_value = Flush.hand_value + hand[0].value + hand[1].value*0.01 + hand[2].value*0.0001 + hand[3].value*0.000001 + hand[4].value*0.00000001

    elif is_straight:
        x = hand[0].value
        if hand[-1].rank == '2':
            x = hand[1].value
        set = Straight
        set_value = Straight.hand_value + x

    elif sorted(list(rank_counts.values()), reverse= True)[0] == 3:
        set = Three_of_a_Kind
        set_value = Three_of_a_Kind.hand_value + hand[2].value

    elif sorted(list(rank_counts.values()), reverse= True)[0] == 2 and sorted(rank_counts.values(), reverse= True)[1] == 2:
        set = Two_Pairs
        set_value = Two_Pairs.hand_value + hand[1].value + hand[3].value*0.01 + 0.00003*hand[0].value + 0.00003*hand[-1].value + 0.00003*hand[2].value

    elif sorted(list(rank_counts.values()), reverse= True)[0] == 2:
        x = 0
        for i in range(1,5):
            if hand[i].value == hand[i - 1].value:
                x = hand[i].value
        set = Pair
        set_value = Pair.hand_value + x

    return set, set_value


def prob_of_win_preflop(start_hand1, start_hand2, sim_number):
    game_deck = [i for i in deck if i not in (start_hand1 + start_hand2)]
    sets = set()
    wins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    draws = 0
    loses = 0

    while len(sets) < sim_number:
        u = tuple(sample(game_deck, 5))
        sets.add(u)


    for i in sets:
        set1 = list(combinations(start_hand1 + list(i), 5))
        set2 = list(combinations(start_hand2 + list(i), 5))

        highest_set1 = "Highest_Card"
        starting_hand_value1 = sorted(start_hand1, key= lambda card: card.value, reverse= True)[0].value + 0.01*sorted(start_hand1, key= lambda card: card.value, reverse= True)[1].value
        starting_hand_value2 = sorted(start_hand2, key= lambda card: card.value, reverse= True)[0].value + 0.01*sorted(start_hand2, key= lambda card: card.value, reverse= True)[1].value
        max_set_value1 = starting_hand_value1
        highest_set2 = "Highest_Card"
        max_set_value2 = starting_hand_value2

        for x in set1:
            check = checking_hand(x)

            if check[1] > max_set_value1:
                max_set_value1 = check[1]
                highest_set1 = check[0].hand_name

        for x in set2:
            check = checking_hand(x)

            if check[1] > max_set_value2:
                max_set_value2 = check[1]
                highest_set2 = check[0].hand_name

        if max_set_value1 > max_set_value2:
            wins[math.floor(max_set_value1)] += 1


        elif max_set_value1 < max_set_value2:
            loses += 1
        else:
            if starting_hand_value1 > starting_hand_value2 and highest_set1 not in ("Two_Pairs", "Four_of_a_Kind", "Highest_Card"):
                wins[math.floor(max_set_value1)] += 1

            elif starting_hand_value1 < starting_hand_value2 and highest_set1 not in ("Two_Pairs", "Four_of_a_Kind", "Highest_Card"):
                loses += 1

            else:
                draws += 1

    return [i.rank for i in start_hand2], wins, draws, loses