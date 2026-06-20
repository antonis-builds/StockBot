import yfinance as yf

ticker = yf.Ticker("MSFT")

data = ticker.history(period="5d")

print(data.tail())