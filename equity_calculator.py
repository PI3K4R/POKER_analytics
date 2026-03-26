from Poker_Tools import Card, deck, simulating_games_from_given_stage, subset_of_db, Preflop, Flop, Turn, River, list_of_opponents
import sqlite3 as sql
import numpy as np

stages = [Flop, Turn, River]
def creating_variables_for_simulation(n, num_of_players: int, card_list: list, sql_con: sql.Cursor) -> list:
    dictionary = {'s': "\u2660", 'd': "\u2666", 'h': "\u2665", 'c': "\u2663"}
    i = 0
    players = []

    while i < num_of_players:
        player = [Card(card_list[i*2][0].upper(), dictionary[card_list[i*2][1]]), Card(card_list[i*2+1][0].upper(), dictionary[card_list[i*2+1][1]])]
        player = sorted(player, key=lambda c: c.value)
        player_db = subset_of_db(n, sql_con, None, player[0].rank, player[1].rank)
        i += 1
        players.append([player, player_db])

    return players

if __name__ == '__main__':
    con = sql.connect("Poker_Database.db")
    cur = con.cursor()

    card_list = input("Podaj karty graczy w formacie 'rank''suit';...: ")
    stage_name = input("Podaj fazę gry (flop, turn, river): ")


    for s in stages:
        if s.stage_name == stage_name:
            stage = s


    dictionary = {'s': "\u2660", 'd': "\u2666", 'h': "\u2665", 'c': "\u2663"}
    cards_revealed = input(f"Podaj {5 - stage.board_unrevealed} cards odkryte w formacie 'rank''suit';'rank''suit'...: ")
    cards_revealed = cards_revealed.split(';')
    cards_revealed = [str(el) for el in cards_revealed]

    i = 5
    while i > stage.board_unrevealed:
        stage.board_revealed.append(Card(cards_revealed[5-i][0].upper(), dictionary[cards_revealed[5-i][1]]))
        i -= 1

    stage.board_revealed = sorted(stage.board_revealed, key=lambda c: c.value)
    card_list = card_list.split(';')
    card_list = [str(el) for el in card_list]

    if len(card_list)%2 != 0:
        print("Number of cards should be odd.")

    elif len(card_list) > 2:
        num_of_players = int(len(card_list)/2)
        print(f"Number of players = {num_of_players}")

        results = simulating_games_from_given_stage(stage, *creating_variables_for_simulation("7", num_of_players, card_list, cur))
        win_equity = sum(results[:-2])/sum(results)
        draws = results[-2]/sum(results)
        print("Win equity: ", round(win_equity*100, 2), "%\n", "Draw % = ", draws*100, "%")

    else:
        checked_hand = creating_variables_for_simulation("7", 1, card_list, cur)
        print(f"Calculating overall equity for {checked_hand[0][0]}...")
        opponents, subset = list_of_opponents("7", checked_hand[0][0], stage.board_revealed, deck, cur)
        results = np.array([0 for _ in range(12)])

        nightmares = []
        for opponent in opponents:
            result = np.array(simulating_games_from_given_stage(stage, checked_hand[0], [opponent, subset]))
            nightmares.append([opponent, np.round(result[-1]/sum(result)*100, 2)])
            results += result

        nightmares = list(sorted(nightmares, key=lambda x: x[1], reverse=True))
        win_equity_overall = sum(results[:-2]) / sum(results)
        draws_overall = results[-2] / sum(results)
        print("Nightmare 60 enemies: \nOpponent   |   Equity")

        for i in range(60):
            print(f"{nightmares[i][0]}   |    {nightmares[i][1]}")

        print(f"\n\n{stage.stage_name.upper()}", "\nWin equity: ", round(win_equity_overall * 100, 2), "%\nDraw % = ",
              round(draws_overall * 100, 2), "%")



