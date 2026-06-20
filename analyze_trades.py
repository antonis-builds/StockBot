import pandas as pd

df = pd.read_csv("trade_log.csv")

sells = df[df["action"] == "SELL"].copy()

print("\n===== TRADE ANALYSIS =====\n")

print("Total closed trades:", len(sells))

wins = sells[sells["profit_pct"] > 0]
losses = sells[sells["profit_pct"] <= 0]

win_rate = len(wins) / len(sells) * 100

print(f"Win Rate: {win_rate:.2f}%")

print(
    f"Average Win: "
    f"{wins['profit_pct'].mean():.2f}%"
)

print(
    f"Average Loss: "
    f"{losses['profit_pct'].mean():.2f}%"
)

print(
    f"Best Trade: "
    f"{sells['profit_pct'].max():.2f}%"
)

print(
    f"Worst Trade: "
    f"{sells['profit_pct'].min():.2f}%"
)

print("\n===== BY SYMBOL =====\n")

summary = (
    sells
    .groupby("symbol")["profit_pct"]
    .agg(["count","mean"])
    .sort_values(
        "mean",
        ascending=False
    )
)

print(summary)