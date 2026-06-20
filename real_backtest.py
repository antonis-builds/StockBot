# ==========================================
# REAL BACKTEST ENGINE
# ------------------------------------------
# Downloads historical market data
# Ranks stocks using analyze_stock()
# Rebalances portfolio every 10 trading days
# Applies stop-loss and trend exits
# Compares performance against QQQ
# ==========================================

# ==========================================
# CONFIGURATION
# ==========================================
import yfinance as yf

from strategy import analyze_stock

import pandas as pd

START_DATE = "2010-01-01"
END_DATE = "2025-12-31"

# ==========================================
# STOCK UNIVERSE
# Large-cap US stocks across sectors
# plus selected international leaders
# ==========================================
stocks = [

    # TECH / AI
    "MSFT","NVDA","AMZN","GOOGL","META",
    "AAPL","TSM","AVGO","NFLX","TSLA",
    "AMD", "ORCL","CRM","ADBE",
    "NOW","INTU","ASML","AMAT","MU",
    "PANW","CRWD","ANET","UBER","SHOP",

    # BANKS
    "JPM","BAC","WFC","GS","MS",
    "C","BLK","SCHW",

    # HEALTHCARE
    "UNH","ABBV","PFE","MRK","LLY",
    "JNJ","TMO","DHR","BMY","ISRG",

    # INDUSTRIALS
    "GE","CAT","DE","HON","RTX",
    "ETN","PH","TT","LMT","NOC",

    # CONSUMER
    "WMT","COST","HD","LOW","MCD",
    "PG","KO","PEP","SBUX","NKE",

    # ENERGY
    "XOM","CVX","COP","SLB","EOG",
    "MPC","PSX","VLO",

    # SEMICONDUCTORS
    "QCOM","TXN","ADI","KLAC","LRCX",
    "ON","MCHP","MPWR",

    # COMMUNICATIONS
    "TMUS","VZ","T","CMCSA","CHTR",

    # FINANCIAL / PAYMENTS
    "V","MA","PYPL","AXP",

    # DEFENSIVE
    "GIS","KMB","CL","MDLZ","HSY",

    # TRANSPORT
    "UNP","CSX","NSC","FDX","UPS",

    # SPECIAL
    "SPXC",
    "000660.KS",
    "SNDR"

]


INITIAL_CAPITAL = 10000
TRADE_COST = 0.001
MAX_POSITIONS = 2

data = {}

# ==========================================
# DOWNLOAD HISTORICAL DATA
# Keep only stocks with at least
# 200 trading days of history
# ==========================================
print("Downloading data...")

for symbol in stocks:

    try:

        df = yf.download(
            symbol,
            start=START_DATE,
            end=END_DATE,
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

# ==========================================
# FIND COMMON TRADING DATES
# Ensures all stocks are evaluated
# on the same rebalance dates
# ==========================================
common_dates = None

for symbol, df in data.items():

    dates = set(df.index)

    if common_dates is None:
        common_dates = dates
    else:
        common_dates &= dates

common_dates = sorted(common_dates)

# ==========================================
# PORTFOLIO STATE
# ==========================================
cash = INITIAL_CAPITAL

positions = {}

portfolio_values = []

trade_count = 0
trade_log = []

# ==========================================
# MAIN BACKTEST LOOP
# Rebalance every 10 trading days
# ==========================================
for i in range(200, len(common_dates), 10):

    current_date = common_dates[i]

    rankings = []

    for symbol, df in data.items():

        try:

            hist = df.loc[:current_date]

            analysis = analyze_stock(hist)

            if analysis is None:
                continue

            rankings.append({
                "symbol": symbol,
                "score": analysis["score"],
                "signal": analysis["signal"]
            })

        except:
            pass


    # Rank all stocks based on
    # strategy score and signal
    rankings.sort(
        key=lambda x: x["score"],
        reverse=True
    )
    # Select BUY candidates
    # ordered by highest score
    buy_list = [
        x["symbol"]
        for x in rankings
        if x["signal"] == "BUY"
    ]
    # ==========================================
    # SELL LOGIC
    # Exit when:
    # 1. Price falls below MA200
    # 2. Stop-loss reaches -15%
    # ==========================================

    # SELL

    for symbol in list(positions.keys()):

        hist = data[symbol].loc[:current_date]

        analysis = analyze_stock(hist)

        price = float(
            data[symbol].loc[current_date]["Close"]
        )

        shares = positions[symbol]["shares"]

        buy_price = positions[symbol]["buy_price"]

        # Calculate unrealized profit/loss
        loss_pct = (
                           (price - buy_price)
                           / buy_price
                   ) * 100

        # Keep position if trend remains
        # intact and stop-loss not triggered
        if (
                price > analysis["ma200"]
                and loss_pct > -15
        ):
            continue

        cash += shares * price * (1 - TRADE_COST)

        profit_pct = (
                             (price - buy_price)
                             / buy_price
                     ) * 100

        if loss_pct <= -15:
            sell_reason = "STOPLOSS"
        else:
            sell_reason = "SIGNAL"

        trade_log.append({
            "date": str(current_date.date()),
            "action": "SELL",
            "symbol": symbol,
            "buy_price": round(buy_price, 2),
            "sell_price": round(price, 2),
            "profit_pct": round(profit_pct, 2),
            "reason": sell_reason
        })

        del positions[symbol]

        trade_count += 1
    # ==========================================
    # BUY LOGIC
    # Fill available portfolio slots
    # with highest-ranked BUY signals
    # ==========================================

    # BUY

    missing = [
        s for s in buy_list
        if s not in positions
    ]

    available_slots = (
            MAX_POSITIONS - len(positions)
    )

    missing = missing[:available_slots]

    # Equal-weight allocation
    # across new positions
    if len(missing) > 0:

        allocation = cash / len(missing)

        for symbol in missing:
            price = float(
                data[symbol].loc[current_date]["Close"]
            )

            shares = (
                             allocation
                             * (1 - TRADE_COST)
                     ) / price

            positions[symbol] = {
                "shares": shares,
                "buy_price": price
            }

            cash -= allocation

            trade_count += 1

    # Calculate current portfolio value
    portfolio_value = cash

    for symbol, position in positions.items():
        shares = position["shares"]

        price = float(
            data[symbol].loc[current_date]["Close"]
        )

        portfolio_value += shares * price

    portfolio_values.append(portfolio_value)

# CLOSE ALL OPEN POSITIONS
# ==========================================
# FORCE CLOSE REMAINING POSITIONS
# Required for final performance
# calculation at backtest end
# ==========================================

if len(positions) > 0:

    last_date = common_dates[-1]

    for symbol in list(positions.keys()):

        price = float(
            data[symbol].loc[last_date]["Close"]
        )

        shares = positions[symbol]["shares"]

        buy_price = positions[symbol]["buy_price"]

        cash += shares * price * (1 - TRADE_COST)

        profit_pct = (
            (price - buy_price)
            / buy_price
        ) * 100

        trade_log.append({
            "date": str(last_date.date()),
            "action": "SELL",
            "symbol": symbol,
            "buy_price": round(buy_price, 2),
            "sell_price": round(price, 2),
            "profit_pct": round(profit_pct, 2),
            "reason": "END_BACKTEST"
        })

        del positions[symbol]

        trade_count += 1

final_value = cash

peak = portfolio_values[0]
max_drawdown = 0

for value in portfolio_values:

    if value > peak:
        peak = value

    drawdown = (
        (peak - value) / peak
    ) * 100

    if drawdown > max_drawdown:
        max_drawdown = drawdown

# ==========================================
# PERFORMANCE METRICS
# Calculate:
# - Final Return
# - Trade Count
# - Max Drawdown
# ==========================================
print()
print("===== REAL BACKTEST =====")
print()

print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
print(f"Final Capital: ${final_value:,.2f}")

print()

print(
    f"Return: "
    f"{((final_value-INITIAL_CAPITAL)/INITIAL_CAPITAL)*100:.2f}%"
)

print(f"Trades: {trade_count}")

print(
    f"Max Drawdown: "
    f"{max_drawdown:.2f}%"
)

print()

print("Current Holdings:")

for symbol in positions:

    print(symbol)

log_df = pd.DataFrame(trade_log)

log_df.to_csv(
    "trade_log.csv",
    index=False
)

qqq = yf.download(
    "QQQ",
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True,
    progress=False
)

if hasattr(qqq.columns, "nlevels") and qqq.columns.nlevels > 1:
    qqq.columns = qqq.columns.get_level_values(0)

start_price = qqq["Close"].iloc[0]
end_price = qqq["Close"].iloc[-1]

qqq_return = (
    (end_price / start_price) - 1
) * 100

print()
print(f"Strategy Return: {((final_value-INITIAL_CAPITAL)/INITIAL_CAPITAL)*100:.2f}%")
print(f"QQQ Return: {qqq_return:.2f}%")

# ==========================================
# TRADE ANALYSIS
# Win rate, average win/loss,
# best trades and worst trades
# ==========================================
wins = log_df[
    (log_df["action"] == "SELL")
    & (log_df["profit_pct"] > 0)
]

losses = log_df[
    (log_df["action"] == "SELL")
    & (log_df["profit_pct"] <= 0)
]

print()
print("SELL TRADES")

print("Wins:", len(wins))
print("Losses:", len(losses))

if len(wins):
    print(
        "Average Win:",
        round(wins["profit_pct"].mean(), 2),
        "%"
    )

if len(losses):
    print(
        "Average Loss:",
        round(losses["profit_pct"].mean(), 2),
        "%"
    )

sells = log_df[
    log_df["action"] == "SELL"
]

print()
print("TOP WINNERS")

print(
    sells.sort_values(
        "profit_pct",
        ascending=False
    )[[
        "symbol",
        "profit_pct",
        "reason"
    ]].head(10)
)

print()
print("TOP LOSERS")

print(
    sells.sort_values(
        "profit_pct"
    )[[
        "symbol",
        "profit_pct",
        "reason"
    ]].head(10)
)

print()
print("Trade log saved.")


