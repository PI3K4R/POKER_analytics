import os
import pandas as pd
from great_tables import GT

ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
root_dir_suited = "C:/Users/Jakub Piekarski/OneDrive/Pulpit/POKER_analytics/Suited"
root_dir_unsuited = "C:/Users/Jakub Piekarski/OneDrive/Pulpit/POKER_analytics/Unsuited"


for i in ranks:
    for j in range(ranks.index(i)+1, len(ranks)):
        j = ranks[j]
        df = pd.DataFrame(
            columns=['type', 'vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins',
                     'Straight_Wins', 'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins' ,'Straight_Flush_Wins',
                     'Royal_Flush_Wins','Draws','Loses', 'Equity_%','Draws_%','Loses_%'])
        for root, dirs, files in os.walk(root_dir_suited):
            for file in files:
                if file == f"{i}_{j}.csv":
                    filepath = os.path.join(root, file)
                    file_df = pd.read_csv(filepath)

                    df = pd.concat([df, file_df])

        df = df.sort_values("Equity_%", ascending=False)[["vs_Hand", "type", "Equity_%", "Draws_%", "Loses_%"]].reset_index(drop=True)
        table = (
            df.style
            .set_caption(f"{i}_{j}")
            .format({
                "Equity_%": "{:.2f}",
                "Draws_%": "{:.2f}",
                "Loses_%": "{:.2f}"
            })
            .background_gradient(cmap="Blues")
        )
        table.to_html(os.path.join(root_dir_suited, "Sorted_equity", f"{i}_{j}.html"))

for i in ranks:
    for j in range(ranks.index(i), len(ranks)):
        j = ranks[j]
        df = pd.DataFrame(
            columns=['type', 'vs_Hand', 'Highest_Card_Wins', 'Pair_Wins', 'Two_Pair_Wins', 'Three_of_a_Kind_Wins',
                     'Straight_Wins', 'Flush_Wins', 'Full_House_Wins', 'Four_of_a_Kind_Wins', 'Straight_Flush_Wins',
                     'Royal_Flush_Wins', 'Draws', 'Loses', 'Equity_%', 'Draws_%', 'Loses_%'])
        for root, dirs, files in os.walk(root_dir_unsuited):
            for file in files:
                if file == f"{i}_{j}.csv":
                    filepath = os.path.join(root, file)
                    file_df = pd.read_csv(filepath)

                    df = pd.concat([df, file_df])

        df = df.sort_values("Equity_%", ascending=False)[["vs_Hand", "type", "Equity_%", "Draws_%", "Loses_%"]].reset_index(drop=True)
        table = (
            df.style
            .set_caption(f"{i}_{j}")
            .format({
                "Equity_%": "{:.2f}",
                "Draws_%": "{:.2f}",
                "Loses_%": "{:.2f}"
            })
            .background_gradient(cmap="Blues")
        )
        table.to_html(os.path.join(root_dir_unsuited, "Sorted_equity", f"{i}_{j}.html"))