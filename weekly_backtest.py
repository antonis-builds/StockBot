import yfinance as yf
import pandas as pd

stocks = [
    "MSFT","NVDA","AMZN","GOOGL","META",
    "AAPL","TSM","AVGO","NFLX","TSLA",
    "AMD","PLTR","ORCL","CRM","ADBE",
    "NOW","INTU","ASML","AMAT","MU",
    "PANW","CRWD","ANET","UBER","SHOP"
]

INITIAL_CAPITAL = 10000

data = {}

print("Downloading data...")

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

        if len(df) >= 200:
            data[symbol] = df

    except Exception as e:

        print(symbol, e)

common_dates = None

for symbol, df in data.items():

    dates = set(df.index)

    if common_dates is None:
        common_dates = dates
    else:
        common_dates = common_dates.intersection(dates)

common_dates = sorted(list(common_dates))

capital = INITIAL_CAPITAL

portfolio = {}

trades = 0

for i in range(200, len(common_dates), 5):

    current_date = common_dates[i]

    rankings = []

    for symbol, df in data.items():

        try:

            hist = df.loc[:current_date]

            if len(hist) < 200:
                continue

            close = float(hist["Close"].iloc[-1])

            ma50 = float(
                hist["Close"].rolling(50).mean().iloc[-1]
            )

            ma200 = float(
                hist["Close"].rolling(200).mean().iloc[-1]
            )

            momentum_3m = (
                (close / float(hist["Close"].iloc[-63])) - 1
            ) * 100

            momentum_6m = (
                (close / float(hist["Close"].iloc[-126])) - 1
            ) * 100

            score = 0

            if close > ma50:
                score += 20

            if close > ma200:
                score += 30

            score += momentum_3m * 0.2
            score += momentum_6m * 0.2

            rankings.append(
                (symbol, score, close, ma50, ma200)
            )

        except:
            pass

    rankings.sort(
        key=lambda x: x[1],
        reverse=True
    )

    top3 = []

    for symbol, score, close, ma50, ma200 in rankings:

        if close > ma50 and ma50 > ma200:

            top3.append(symbol)

        if len(top3) == 3:
            break

    if len(top3) == 0:
        continue

    portfolio = set(top3)

    trades += 1

final_holdings = list(portfolio)

if len(final_holdings) > 0:

    allocation = capital / len(final_holdings)

    final_value = 0

    last_date = common_dates[-1]

    for symbol in final_holdings:

        df = data[symbol]

        current_price = float(
            df.loc[last_date]["Close"]
        )

        final_value += allocation

else:

    final_value = capital

print()
print("===== WEEKLY BACKTEST =====")
print()

print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
print(f"Final Capital: ${final_value:,.2f}")

print()

print(
    f"Return: "
    f"{((final_value-INITIAL_CAPITAL)/INITIAL_CAPITAL)*100:.2f}%"
)

print(f"Rebalances: {trades}")

print()
print("Final Portfolio:")
print(final_holdings)