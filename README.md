NSE Stock Screener with Technical Indicators

Overview
This Python project is a stock screener for NSE-listed companies. It fetches live stock listings from the National Stock Exchange (NSE) using nsetools, downloads historical OHLCV (Open, High, Low, Close, Volume) data via yfinance, and applies customizable technical analysis formulas to identify potential trading opportunities.
The screener supports multiple technical indicators such as SMA and EMA crossovers, RSI thresholds, and volume-based filters. All formulas are stored in a separate file (stock_market_formulas.txt), making it easy to add or modify strategies without changing the main script.

The output is a clean, easy-to-read Pandas DataFrame that lists:
Stock Name,Latest Price,Percentage Change,Volume,Direct link to a TradingView chart
This setup allows you to analyze all NSE-listed stocks dynamically, as the stock list is scraped live.

Requirements
Python 3.10+
Libraries:
nsetools – to fetch live NSE stock listings
yfinance – to download historical stock data
pandas – for data handling and analysis
inspect – for dynamic formula loading
os – for file operations
