import locale
import pandas as pd
from luno_python.client import Client
from ta import add_all_ta_features
import logging
import os

# Set locale to format numbers with thousands separators
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Your Luno API key and secret (consider using environment variables for security)
API_KEY = os.getenv('LUNO_API_KEY', 'your_api_key_here')
API_SECRET = os.getenv('LUNO_API_SECRET', 'your_api_secret_here')

# Initialize the Luno client
client = Client(api_key_id=API_KEY, api_key_secret=API_SECRET)

# Track initial investments
initial_investments = {
    'XRP': {'amount_invested': 50, 'units_held': 5},
    'XBT': {'amount_invested': 25, 'units_held': 0.0000592},
    'ETH': {'amount_invested': 25, 'units_held': 0.00157}
}

def get_market_data(pair):
    try:
        orderbook = client.get_order_book(pair)
        return orderbook
    except Exception as e:
        logging.error(f"Error fetching data for {pair}: {e}")
        return None

def get_historical_data(pair, limit=100):
    try:
        # Fetch historical trades for analysis
        trades = client.get_trades(pair, limit=limit)
        return pd.DataFrame(trades['trades'])
    except Exception as e:
        logging.error(f"Error fetching historical data for {pair}: {e}")
        return None

def calculate_rsi(data, period=14):
    if len(data) < period:
        logging.warning("Not enough data to calculate RSI.")
        return None

    data['rsi'] = data['close'].rolling(window=period).apply(
        lambda x: 100 - (100 / (1 + (x.iloc[-1] / x.mean()))), raw=False
    )
    return data

def analyze_market(pair):
    orderbook = get_market_data(pair)
    if orderbook:
        historical_data = get_historical_data(pair)
        if historical_data is not None:
            historical_data['close'] = historical_data['price']  # Assume 'price' is the closing price
            historical_data = calculate_rsi(historical_data)

            if historical_data['rsi'].isnull().all():
                logging.warning(f"RSI could not be calculated for {pair}. Not enough data.")
                return

            latest_rsi = historical_data['rsi'].iloc[-1]
            logging.info(f"Latest RSI for {pair}: {latest_rsi}")

            # Example decision based on RSI
            if latest_rsi < 30:
                logging.info(f"Buy signal for {pair}")
                # Execute buy logic here
            elif latest_rsi > 70:
                logging.info(f"Sell signal for {pair}")
                # Execute sell logic here
            else:
                logging.info(f"No action for {pair}")
        else:
            logging.warning(f"Skipping analysis for {pair} due to no historical data.")
    else:
        logging.warning(f"Skipping analysis for {pair} due to market unavailability.")

def main():
    pairs = ['XRPMYR', 'XBTMYR', 'ETHMYR']
    for pair in pairs:
        logging.info(f"\nAnalyzing {pair}...")
        analyze_market(pair)

if __name__ == "__main__":
    main()