import pandas as pd


def calculate_rsi(close, period=14):

    delta = close.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1])


def signal(close, ma50, ma200, rsi):

    if close > ma50 and ma50 > ma200 and 45 <= rsi <= 80:
        return "BUY"

    if close > ma200:
        return "HOLD"

    return "AVOID"


def calculate_score(
    close,
    ma50,
    ma200,
    rsi,
    momentum_3m,
    momentum_6m,

):

    score = 0

    if close > ma50:
        score += 10

    if close > ma200:
        score += 20

    score += momentum_3m * 0.2
    score += momentum_6m * 0.3


    if 45 <= rsi <= 80:
        score += 10

    return round(score, 2)


def analyze_stock(df):

    df = df.dropna()

    if len(df) < 200:
        return None

    close = float(df["Close"].iloc[-1])

    ma50 = float(
        df["Close"].rolling(50).mean().iloc[-1]
    )

    ma200 = float(
        df["Close"].rolling(200).mean().iloc[-1]
    )

    rsi = calculate_rsi(df["Close"])

    momentum_3m = (
        (close / float(df["Close"].iloc[-63])) - 1
    ) * 100

    momentum_6m = (
        (close / float(df["Close"].iloc[-126])) - 1
    ) * 100


    score = calculate_score(
        close,
        ma50,
        ma200,
        rsi,
        momentum_3m,
        momentum_6m,

    )

    trade_signal = signal(
        close,
        ma50,
        ma200,
        rsi
    )

    return {
        "price": round(close, 2),
        "ma50": round(ma50, 2),
        "ma200": round(ma200, 2),
        "rsi": round(rsi, 2),
        "score": round(score, 2),
        "signal": trade_signal
    }