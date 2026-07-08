import pandas as pd
import os

ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

root_dir_suited = "C:/Users/Jakub Piekarski/OneDrive/Pulpit/Poker_data/POKER_analytics/Suited"
root_dir_unsuited = "C:/Users/Jakub Piekarski/OneDrive/Pulpit/Poker_data/POKER_analytics/Unsuited"

for idxi, i in enumerate(ranks):
    for idx, j in enumerate(ranks[ranks.index(i)+1:]):
        idxj = idx + ranks.index(i) + 1
        for root, dirs, files in os.walk(root_dir_suited):
                for file in files:
                    if file == f"{i}_{j}.csv":
                        filepath = os.path.join(root, file)
                        df = pd.read_csv(filepath, index_col="vs_Hand")
                        sum_wins = df.filter(like="Wins").sum().sum()
                        sum_loses = df["Loses"].sum()
                        sum_draws = df["Draws"].sum()

                        dangerous_opponents = df["Equity_%"].sort_values().head(10)
                        print(dangerous_opponents)