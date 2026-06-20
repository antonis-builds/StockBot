import yfinance as yf

symbol = "TSM"

initial_capital = 10000

df = yf.download(
    symbol,
    period="5y",
    auto_adjust=True,
    progress=False
)

if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
    df.columns = df.columns.get_level_values(0)

df = df.dropna()

buy_price = df["Close"].iloc[0]
last_price = df["Close"].iloc[-1]

shares = initial_capital / buy_price

final_value = shares * last_price

return_pct = (
    (final_value - initial_capital)
    / initial_capital
) * 100

print()
print("===== SIMPLE BACKTEST =====")
print()

print(f"Symbol: {symbol}")
print(f"Buy Price: {buy_price:.2f}")
print(f"Current Price: {last_price:.2f}")

print()

print(f"Initial Capital: ${initial_capital:,.2f}")
print(f"Final Capital: ${final_value:,.2f}")

print()

print(f"Return: {return_pct:.2f}%")