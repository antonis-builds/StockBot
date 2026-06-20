# StockBot

A Python stock screening and backtesting system.

## Features

* RSI (14)
* MA50 / MA200 trend analysis
* Momentum ranking
* Stop-loss protection
* Portfolio backtesting
* QQQ benchmark comparison
* Trade performance analytics

## Strategy Logic

The system ranks stocks based on:

* Trend strength
* Relative momentum
* RSI filter
* Moving average confirmation

The highest ranked stocks are selected and managed through predefined buy and sell rules.

## Files

* `main.py` - Stock scanner
* `strategy.py` - Signal generation
* `stock_ranker.py` - Ranking engine
* `real_backtest.py` - Portfolio backtesting
* `benchmark_compare.py` - QQQ comparison
* `analyze_trades.py` - Trade analysis

## Example Results

Example backtest:

* Initial Capital: $10,000
* Final Capital: $59,097
* Return: 490.97%

## Author

Antonis
