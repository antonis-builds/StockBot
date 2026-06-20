import yfinance as yf

for symbol in ["QQQ", "SPY"]:

    df = yf.download(
        symbol,
        start="2023-01-01",
        auto_adjust=True,
        progress=False
    )

    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)

    start_price = df["Close"].iloc[0]
    end_price = df["Close"].iloc[-1]

    ret = ((end_price / start_price) - 1) * 100

    print(
        f"{symbol} | Return={ret:.2f}%"
    )