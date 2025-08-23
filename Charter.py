from nsetools import Nse
import yfinance as yf
import pandas as pd
import inspect
import os

# ========= Helpers available to your formulas =========
def sma(series, n):  # Simple Moving Average
    return series.rolling(int(n)).mean()

def ema(series, n):  # Exponential Moving Average
    return series.ewm(span=int(n), adjust=False).mean()

def rsi(series, period=14):
    period = int(period)
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(period).mean()
    roll_down = down.rolling(period).mean()
    rs = roll_up / roll_down
    return 100 - (100 / (1 + rs))

def highest(series, n):
    return series.rolling(int(n)).max()

def lowest(series, n):
    return series.rolling(int(n)).min()
# ======================================================

FORMULA_FILE = "stock_market_formulas.txt"  # put your formula functions here
CHOSEN_FORMULA = None                      # e.g. "sma_crossover"; if None, you'll be prompted

def load_formulas(path=FORMULA_FILE):
    if not os.path.exists(path):
        raise FileNotFoundError(f"'{path}' not found. Create it with your formula functions.")

    env = {
        "pd": pd,
        "sma": sma, "ema": ema, "rsi": rsi,
        "highest": highest, "lowest": lowest,
    }
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, env)
    funcs = {
        name: obj for name, obj in env.items()
        if callable(obj) and name not in ["sma","ema","rsi","highest","lowest"]
    }
    if not funcs:
        raise ValueError("No functions found in stock_market_formulas.txt.")
    return funcs


# Step 1: Get NSE stock list
nse = Nse()
all_stocks = nse.get_stock_codes()
symbols = all_stocks[1:]  # skip "SYMBOL"
tickers = [s + ".NS" for s in symbols]

# Add these two lines
total_listings = len(symbols)
print("Total NSE listings:", total_listings)


# Step 2: Download OHLCV data
data = yf.download(tickers[:total_listings], period="6mo", interval="1d", auto_adjust=False) #CHANGE LISTING NUMBER HERE

open_data   = data["Open"]
high_data   = data["High"]
low_data    = data["Low"]
close_data  = data["Close"]
volume_data = data["Volume"]

# Load formulas
formulas = load_formulas(FORMULA_FILE)
if CHOSEN_FORMULA is None:
    print("Available formulas:", list(formulas.keys()))
    chosen_name = input("Choose formula: ").strip()
else:
    chosen_name = CHOSEN_FORMULA

if chosen_name not in formulas:
    raise ValueError(f"Formula '{chosen_name}' not found. Available: {list(formulas.keys())}")

formula_func = formulas[chosen_name]
sig = inspect.signature(formula_func)
needed_params = list(sig.parameters.keys())

results = []

# Step 4: Apply chosen formula
for ticker in close_data.columns:
    symbol = ticker.replace(".NS", "")

    hist = pd.concat([
        open_data[ticker].rename("open"),
        high_data[ticker].rename("high"),
        low_data[ticker].rename("low"),
        close_data[ticker].rename("close"),
        volume_data[ticker].rename("volume")
    ], axis=1).dropna()

    if hist.empty:
        continue

    # Build kwargs only for OHLCV
    argmap = {}
    for p in needed_params:
        if p in ["open","high","low","close","volume"]:
            argmap[p] = hist[p]

    try:
        ok = bool(formula_func(**argmap))
    except Exception:
        continue

    if ok:
        latest_price = hist["close"].iloc[-1]
        prev_price = hist["close"].iloc[-2] if len(hist) > 1 else latest_price
        pct_change = ((latest_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        latest_vol = int(hist["volume"].iloc[-1])

        results.append({
            "Stock Name": symbol,
            "% Chg": round(pct_change, 2),
            "Price": round(float(latest_price), 2),
            "Volume": latest_vol,
            "Links": f"https://www.tradingview.com/chart/?symbol=NSE:{symbol}"
        })

# Step 5: DataFrame
df = pd.DataFrame(results)
if not df.empty:
    df = df.sort_values(by="Price", ascending=False).reset_index(drop=True)
    # Add Sr. column starting from 1
    df.insert(0, "Sr.", range(1, len(df) + 1))

print(f"Stocks satisfying '{chosen_name}' (sorted by latest price):")
if not df.empty:
    # Print without the pandas default index
    print(df.to_string(index=False))
else:
    print("No matches.")
