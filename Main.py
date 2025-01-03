import os
import smtplib
from email.mime.text import MIMEText
import yfinance as yf
import requests
import pandas as pd


# Fetch News Headlines
def fetch_news(stock_symbol, api_key):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={api_key}"
    response = requests.get(url)
    articles = response.json().get("articles", [])

    headlines = []
    for article in articles[:3]:  # Get top 3 headlines
        headlines.append(f"<li><a href='{article['url']}'>{article['title']}</a></li>")
    return "\n".join(headlines)


def calculate_market_bias(ticker):
    # Fetch data for the stock
    try:
        data = yf.download(ticker, period="1d", interval="1d")  # Change period to '1d'
        
        if data.empty:
            print(f"No data returned for {ticker}")
            return None, None, "No Data"
        
        # Extract today's open and yesterday's close as scalars
        today_open = data['Open'].iloc[0]  # Open price for today
        yesterday_close = data['Close'].iloc[0]  # Close price from the last available day
        
        # Determine the market bias
        if today_open > yesterday_close:
            bias = "Bullish"
        elif today_open < yesterday_close:
            bias = "Bearish"
        else:
            bias = "Neutral"
        
        return today_open, yesterday_close, bias
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None, "Error"


# Generate Email Content
def generate_email_content():
    api_key = os.getenv("news_api_key")

    # List of stocks to fetch news for
    watchlist = ["AAPL", "TSLA", "GOOG"]
    watchlist_news = ""

    # Generate Watchlist News
    for stock in watchlist:
        news = fetch_news(stock, api_key)
        watchlist_news += f"<h3>{stock} News:</h3><ul>{news}</ul>"

    # Add Market Bias Analysis for S&P 500 (VUSA)
    ticker = "VUSA.L"
    latest_open, latest_close, bias = calculate_market_bias(ticker)  # Updated for 3 values
    market_summary = f"""
    <h3>Market Bias for {ticker}:</h3>
    <p>Latest Open: {latest_open}</p>
    <p>Latest Close: {latest_close}</p>
    <p><strong>Market Bias: {bias}</strong></p>
    """

    # Create Email HTML
    email_body = f"""
    <html>
    <head>
        <style>
        body {{ font-family: Arial, sans-serif; }}
        h1 {{ color: #c1c1ce; }}
        h3 {{ color: #0073e6; }}
        </style>
    </head>
    <body>
        <h1>Daily Market Summary</h1>
        <h2>Watchlist News:</h2>
        {watchlist_news}
        {market_summary}
    </body>
    </html>
    """

    return email_body


# Send Email
def send_email(subject, body):
    from_email = "nylewagjiani@gmail.com"
    to_email = "nylewagjiani@gmail.com"
    password = os.getenv("password")

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())


# Main Function
def main():
    # Generate email content
    email_body = generate_email_content()

    # Send the email
    send_email("Daily Market Summary", email_body)


if __name__ == "__main__":
    main()
