import yfinance as yf
import pandas as pd

stocks = [
    "MSFT","NVDA","AMZN","GOOGL","META",
    "AAPL","TSM","AVGO","NFLX","TSLA",
    "AMD","PLTR","ORCL","CRM","ADBE",
    "NOW","INTU","ASML","AMAT","MU",
    "PANW","CRWD","ANET","UBER","SHOP"
]

capital = 10000
best_stock = None

results = []

for symbol in stocks:

    try:

        df = yf.download(
            symbol,
            period="5y",
            auto_adjust=True,
            progress=False
        )

        if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()

        if len(df) < 200:
            continue

        start_price = float(df["Close"].iloc[0])
        end_price = float(df["Close"].iloc[-1])

        return_pct = (
            (end_price - start_price)
            / start_price
        ) * 100

        final_value = capital * (1 + return_pct / 100)

        results.append({
            "symbol": symbol,
            "return": round(return_pct, 2),
            "final": round(final_value, 2)
        })

    except Exception as e:

        print(symbol, e)

results = sorted(
    results,
    key=lambda x: x["return"],
    reverse=True
)

print("\n===== 5 YEAR RANKING =====\n")

for i, stock in enumerate(results[:10], start=1):

    print(
        f"{i}. "
        f"{stock['symbol']} "
        f"Return={stock['return']}% "
        f"Final=${stock['final']:,.2f}"
    )

winner = results[0]

print("\n===== BEST STOCK =====\n")

print(
    f"{winner['symbol']} "
    f"Return={winner['return']}% "
    f"Final=${winner['final']:,.2f}"
)