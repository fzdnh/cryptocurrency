import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import matplotlib.pyplot as plt
import locale
from luno_python.client import Client
from datetime import datetime

# Set locale to format numbers with thousands separators
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Your Luno API key and secret
API_KEY = 'nny55x3562h54'
API_SECRET = 'ZgSqn4BXbryRcsLIOaQ-6jZimZOxOaYLbKkdUK122iE'

# Initialize the Luno client
client = Client(api_key_id=API_KEY, api_key_secret=API_SECRET)

# Function to get cryptocurrency prices from Luno in MYR
def get_crypto_prices():
    prices = {}
    pairs = ['XRPMYR', 'XBTMYR', 'ETHMYR']
    
    for pair in pairs:
        try:
            orderbook = client.get_ticker(pair=pair)
            if isinstance(orderbook, dict) and 'ask' in orderbook:
                prices[pair[:3]] = float(orderbook['ask'])
        except Exception as e:
            print(f"Error fetching data for {pair}: {e}")

    return prices

# Function to format the price in RM with commas and two decimal points
def format_price(price):
    return f"RM {locale.format_string('%.2f', price, grouping=True)}"

# Function to load investments from a JSON file
def load_investments():
    try:
        with open('investments.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Function to save investments to a JSON file
def save_investments(investments):
    with open('investments.json', 'w') as f:
        json.dump(investments, f)

# Function to collect investment data
def collect_investment_data():
    investments = []
    for crypto in ['XRP', 'XBT', 'ETH']:
        amount_invested = simpledialog.askfloat("Input", f"Enter amount invested for {crypto}:")
        price_per_unit = simpledialog.askfloat("Input", f"Enter price per unit for {crypto}:")
        if amount_invested is not None and price_per_unit is not None:
            units_held = amount_invested / price_per_unit
            investments.append({
                'crypto': crypto,
                'amount_invested': amount_invested,
                'price_per_unit': price_per_unit,
                'units_held': units_held,
                'date': datetime.now().isoformat()  # Store the current date and time
            })
    return investments

# Function to display investment results
def display_investment_results(investments, prices):
    for investment in investments:
        crypto = investment['crypto']
        amount_invested = investment['amount_invested']
        units_held = investment['units_held']
        current_price = prices.get(crypto)
        
        if current_price is not None:
            current_value = current_price * units_held
            profit_loss = current_value - amount_invested
            profit_loss_percentage = (profit_loss / amount_invested) * 100 if amount_invested > 0 else 0
            
            messagebox.showinfo("Investment Result", 
                f"{crypto} Investment:\n"
                f"  Amount Invested: {format_price(amount_invested)}\n"
                f"  Current Price per Unit: {format_price(current_price)}\n"
                f"  Units Held: {units_held:.8f}\n"
                f"  Current Value: {format_price(current_value)}\n"
                f"  Profit/Loss: {format_price(profit_loss)}\n"
                f"  Profit/Loss Percentage: {profit_loss_percentage:.2f}%"
            )

# Function to plot investment data
def plot_investments(investments):
    # Prepare data for plotting
    dates = []
    crypto_data = {'XRP': [], 'XBT': [], 'ETH': []}

    # Collect profit/loss percentages for each investment
    for investment in investments:
        crypto = investment['crypto']
        date = datetime.fromisoformat(investment['date'])
        
        # Only add the date once
        if date not in dates:
            dates.append(date)

        current_price = get_crypto_prices().get(crypto)
        
        if current_price is not None:
            current_value = current_price * investment['units_held']
            profit_loss = current_value - investment['amount_invested']
            profit_loss_percentage = (profit_loss / investment['amount_invested']) * 100 if investment['amount_invested'] > 0 else 0
            
            # Append the profit/loss percentage to the corresponding cryptocurrency
            crypto_data[crypto].append(profit_loss_percentage)

    # Ensure all cryptocurrencies have the same number of dates for plotting
    for key in crypto_data:
        while len(crypto_data[key]) < len(dates):
            crypto_data[key].append(None)  # Fill with None for missing data

    plt.figure(figsize=(10, 5))
    
    # Plot each cryptocurrency's data
    plt.plot(dates, crypto_data['XRP'], marker='o', label='XRP')
    plt.plot(dates, crypto_data['XBT'], marker='o', label='XBT')
    plt.plot(dates, crypto_data['ETH'], marker='o', label='ETH')

    plt.title('Investment Profit/Loss Percentage Over Time')
    plt.xlabel('Date')
    plt.ylabel('Profit/Loss Percentage (%)')
    
    # Format the x-axis to show only month and year
    plt.xticks(rotation=45)
    plt.gca().set_xticks(dates)
    plt.gca().set_xticklabels([date.strftime('%b %Y') for date in dates])
    
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

# Main function to run the application
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Load previous investments
    investments = load_investments()

    # Collect new investment data
    new_investments = collect_investment_data()
    investments.extend(new_investments)

    # Save all investments
    save_investments(investments)

    # Get current cryptocurrency prices
    prices = get_crypto_prices()

    # Display investment results
    display_investment_results(investments, prices)

    # Plot the investments
    plot_investments(investments)

    root.mainloop()

if __name__ == "__main__":
    main()