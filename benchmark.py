import yfinance as yf

symbols = [
    "QQQ",
    "SPY",
    "NVDA",
    "MU"
]

capital = 10000

print("\n===== BENCHMARK =====\n")

for symbol in symbols:

    df = yf.download(
        symbol,
        period="10y",
        auto_adjust=True,
        progress=False
    )

    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()

    start_price = float(df["Close"].iloc[0])
    end_price = float(df["Close"].iloc[-1])

    shares = capital / start_price

    final_value = shares * end_price

    ret = (
        (final_value - capital)
        / capital
    ) * 100

    print(
        f"{symbol} | "
        f"Final=${final_value:,.2f} | "
        f"Return={ret:.2f}%"
    )