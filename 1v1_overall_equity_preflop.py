import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import seaborn as sns

ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
root_dir_suited = "C:/Users/Jakub Piekarski/OneDrive/Pulpit/Poker_data/POKER_analytics/Suited" #your default path
root_dir_unsuited = "C:/Users/Jakub Piekarski/OneDrive/Pulpit/Poker_data/POKER_analytics/Unsuited" #your default path
grid = np.zeros((len(ranks), len(ranks)))


# Suited
fig = plt.figure(figsize=(20, 30))
for idxi, i in enumerate(ranks):
    for idx, j in enumerate(ranks[ranks.index(i)+1:]):
        idxj = idx + ranks.index(i) + 1
        for root, dirs, files in os.walk(root_dir_suited):
                for file in files:
                    if file == f"{i}_{j}.csv":
                        filepath = os.path.join(root, file)
                        df = pd.read_csv(filepath, index_col = "vs_Hand")
                        sum_wins = df.filter(like="Wins").sum().sum()
                        sum_loses = df["Loses"].sum()
                        sum_draws = df["Draws"].sum()


        overall_equity = sum_wins/(sum_wins + sum_loses)*100
        grid[ranks.index(i), ranks.index(j)] = overall_equity

        ax = plt.subplot2grid(shape=(13, 13), loc=(idxi, idxj), fig=fig)
        ax.hist(df["Equity_%"], bins=20, range=(0, 100))
        ax.set_title(f"{i}{j}")

plt.tight_layout()
plt.show()


grid = grid.T
mask = np.triu(np.ones_like(grid, dtype=bool), k=0)

plt.figure(figsize=(30, 20))
sns.heatmap(
    grid,
    mask=mask,
    cmap="viridis",
    xticklabels=ranks,
    yticklabels=ranks,
    square=True,
    annot=True,
    fmt=".1f",
    cbar_kws={"label": "Total Equity"}
)

plt.title("Equity Heatmap Suited")
plt.show()
plt.savefig("Overall_equity_Suited")

# Unsuited
fig_un = plt.figure(figsize=(20, 30))
for idxi, i in enumerate(ranks):
    for idx, j in enumerate(ranks[ranks.index(i):]):
        idxj = idx + ranks.index(i)
        for root, dirs, files in os.walk(root_dir_unsuited):
                for file in files:
                    if file == f"{i}_{j}.csv":
                        filepath = os.path.join(root, file)
                        df = pd.read_csv(filepath, index_col = "vs_Hand")
                        sum_wins = df.filter(like="Wins").sum().sum()
                        sum_loses = df["Loses"].sum()
                        sum_draws = df["Draws"].sum()


        overall_equity = sum_wins/(sum_wins + sum_loses)*100
        grid[ranks.index(i), ranks.index(j)] = overall_equity

        ax_un = plt.subplot2grid(shape=(13, 13), loc=(idxi, idxj), fig=fig_un)
        ax_un.hist(df["Equity_%"], bins=20, range=(0, 100))
        ax_un.set_title(f"{i}{j}")

plt.tight_layout()
plt.show()

grid = grid.T
mask = np.triu(np.ones_like(grid, dtype=bool), k=1)

plt.figure(figsize=(15, 10))
sns.heatmap(
    grid,
    mask=mask,
    cmap="viridis",
    xticklabels=ranks,
    yticklabels=ranks,
    square=True,
    annot=True,
    fmt=".1f",
    cbar_kws={"label": "Total Equity"}
)

plt.title("Equity Heatmap Unsuited")
plt.show()
plt.savefig("Overall_Equity_Unsuited")