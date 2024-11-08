import pandas as pd
from flask import Flask, request, render_template, send_file
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import os
# Initialize Flask app
app = Flask(__name__)

# API Key for Alpha Vantage
api_key = "A5XGJKIF1F4259FR"

# Load stock symbols from the Excel file

def load_stock_symbols():
    filepath = "/mnt/data/stocks.csv"  # Path inside the Docker container
    try:
        df = pd.read_csv(filepath)
        symbols = df['Symbol'].tolist()  
        return symbols
    except Exception as e:
        print(f"Error loading stock symbols: {e}")
        return []

# Stock symbols list
stock_symbols = load_stock_symbols()

# Fetch stock data function
def fetch_stock_data(symbol, time_series_function, interval=None):
    url = "https://www.alphavantage.co/query"
    params = {
        'function': time_series_function,
        'symbol': symbol,
        'apikey': api_key,
        'outputsize': 'compact'  
    }

    if time_series_function == "TIME_SERIES_INTRADAY" and interval:
        params['interval'] = interval

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "Error Message" in data or "Note" in data:
            return None
        return data
    else:
        print("Error fetching data from API.")
        return None

# Parse data for plotting
def parse_data(data, time_series_function, start_date, end_date, interval=None):
    time_series_key = {
        "TIME_SERIES_INTRADAY": f"Time Series ({interval})",
        "TIME_SERIES_DAILY": "Time Series (Daily)",
        "TIME_SERIES_WEEKLY": "Weekly Time Series",
        "TIME_SERIES_MONTHLY": "Monthly Time Series"
    }.get(time_series_function, "Time Series (Daily)")

    if time_series_key not in data:
        return [], [], [], [], []

    time_series_data = data[time_series_key]
    dates, opens, highs, lows, closes = [], [], [], [], []

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    for date_str, values in time_series_data.items():
        if time_series_function == "TIME_SERIES_INTRADAY":
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')  # Include both date and time for intraday
        else:
            date = datetime.strptime(date_str, '%Y-%m-%d')

        if start <= date <= end:
            dates.append(date)
            opens.append(float(values["1. open"]))
            highs.append(float(values["2. high"]))
            lows.append(float(values["3. low"]))
            closes.append(float(values["4. close"]))

    # Ensure dates are sorted for chronological order
    dates, opens, highs, lows, closes = zip(*sorted(zip(dates, opens, highs, lows, closes)))
    return dates, opens, highs, lows, closes

# Generate chart function
def generate_chart(dates, opens, highs, lows, closes, symbol, chart_type, start_date, end_date):
    plt.figure(figsize=(10, 5))

    if chart_type == "bar":
        # Bar width and indices for each date
        bar_width = 0.2
        indices = np.arange(len(dates))  # Using actual dates length for alignment

        # Plot grouped bars with offsets
        plt.bar(indices - bar_width*1.5, opens, bar_width, label='Open', color='blue', alpha=0.7)
        plt.bar(indices - bar_width*0.5, highs, bar_width, label='High', color='green', alpha=0.7)
        plt.bar(indices + bar_width*0.5, lows, bar_width, label='Low', color='red', alpha=0.7)
        plt.bar(indices + bar_width*1.5, closes, bar_width, label='Close', color='purple', alpha=0.7)

        # Map x-axis ticks to actual dates
        plt.xticks(indices, [date.strftime("%Y-%m-%d") for date in dates], rotation=45)
    else:
        # Line plot for each type
        plt.plot(dates, opens, label='Open', color='blue', marker='o')
        plt.plot(dates, highs, label='High', color='green', marker='^')
        plt.plot(dates, lows, label='Low', color='red', marker='v')
        plt.plot(dates, closes, label='Close', color='purple', marker='s')

        plt.xticks(rotation=45)

    # Add titles, labels, and legend
    plt.title(f"Stock Prices for {symbol} ({start_date} to {end_date})")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the chart as a PNG
    chart_filename = "static/stock_chart.png"
    plt.savefig(chart_filename)
    plt.close()
    return chart_filename

# Define routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        symbol = request.form["symbol"]
        chart_type = request.form["chart_type"]
        time_series_function = request.form["time_series_function"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        interval = request.form.get("interval", None)

        # Fetch and process data
        stock_data = fetch_stock_data(symbol, time_series_function, interval)
        if stock_data:
            dates, opens, highs, lows, closes = parse_data(stock_data, time_series_function, start_date, end_date, interval)
            if dates:
                chart_path = generate_chart(dates, opens, highs, lows, closes, symbol, chart_type, start_date, end_date)
                return render_template("index.html", chart_path=chart_path, symbols=stock_symbols)
            else:
                error = "No data found for the given date range."
                return render_template("index.html", error=error, symbols=stock_symbols)
        else:
            error = "Failed to fetch data from API."
            return render_template("index.html", error=error, symbols=stock_symbols)
    return render_template("index.html", symbols=stock_symbols)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)