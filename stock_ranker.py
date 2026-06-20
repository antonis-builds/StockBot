import yfinance as yf
import json
import os

from strategy import analyze_stock

stocks = [
    "MSFT","NVDA","AMZN","GOOGL","META",
    "AAPL","TSM","AVGO","NFLX","TSLA",
    "AMD","PLTR","ORCL","CRM","ADBE",
    "NOW","INTU","ASML","AMAT","MU",
    "PANW","CRWD","ANET","UBER","SHOP"
]

results = []

for symbol in stocks:

    try:

        df = yf.download(
            symbol,
            period="1y",
            progress=False,
            auto_adjust=True
        )

        if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()

        if len(df) < 200:
            continue

        analysis = analyze_stock(df)

        if analysis is None:
            continue

        results.append({
            "symbol": symbol,
            "score": analysis["score"],
            "price": analysis["price"],
            "rsi": analysis["rsi"],
            "signal": analysis["signal"]
        })

    except Exception as e:

        print(symbol, e)

results = sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
)

print("\n===== STOCK RANKING =====\n")

for i, stock in enumerate(results, start=1):

    print(
        f"{i}. "
        f"{stock['symbol']} "
        f"Signal={stock['signal']} "
        f"Score={stock['score']} "
        f"RSI={stock['rsi']} "
        f"Price={stock['price']}"
    )

portfolio_file = "portfolio.json"

if os.path.exists(portfolio_file):

    with open(portfolio_file, "r") as f:
        portfolio = json.load(f)

else:

    portfolio = {
        "positions": {}
    }

positions = portfolio["positions"]

top_buy_stocks = [
    stock
    for stock in results
    if stock["signal"] == "BUY"
][:3]

buy_candidates = {
    stock["symbol"]: stock
    for stock in top_buy_stocks
}
print("\n===== PORTFOLIO STATUS =====\n")

for symbol in list(positions.keys()):

    if symbol not in buy_candidates:

        print(f"SELL -> {symbol} (SIGNAL LOST)")

        del positions[symbol]

        continue

    current_price = buy_candidates[symbol]["price"]
    buy_price = positions[symbol]["buy_price"]

    profit_pct = (
        (current_price - buy_price)
        / buy_price
    ) * 100

    print(
        f"{symbol} | "
        f"Buy={buy_price} | "
        f"Now={current_price} | "
        f"P/L={profit_pct:.2f}%"
    )

    if profit_pct <= -10:

        print(
            f"SELL -> {symbol} "
            f"(STOP LOSS)"
        )

        del positions[symbol]

        continue

    if profit_pct >= 25:

        print(
            f"SELL -> {symbol} "
            f"(TAKE PROFIT)"
        )

        del positions[symbol]

        continue

for symbol, stock in buy_candidates.items():

    if symbol not in positions:

        positions[symbol] = {
            "buy_price": stock["price"]
        }

        print(
            f"BUY -> {symbol} "
            f"at {stock['price']}"
        )

with open(portfolio_file, "w") as f:

    json.dump(
        portfolio,
        f,
        indent=4
    )

print("\nPortfolio saved.")