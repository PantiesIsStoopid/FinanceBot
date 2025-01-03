import os
import smtplib
from email.mime.text import MIMEText
import yfinance as yf
import requests

# Fetch News Headlines
def fetch_news(stock_symbol, api_key):
    url = f'https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={api_key}'
    response = requests.get(url)
    articles = response.json().get('articles', [])

    headlines = []
    for article in articles[:3]:  # Get top 3 headlines
        headlines.append(f"<li><a href='{article['url']}'>{article['title']}</a></li>")
    return '\n'.join(headlines)

# Calculate Market Bias using EMA
def calculate_market_bias(ticker):
    data = yf.download(ticker, period='1d', interval='1d')

    # Calculate the EMAs (e.g., 50-day and 200-day)
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()

    # Get the latest price and EMAs
    latest_close = data['Close'].iloc[-1]
    latest_ema50 = data['EMA50'].iloc[-1]
    latest_ema200 = data['EMA200'].iloc[-1]

    # Determine market bias based on the relationship between price and EMAs
    if latest_close > latest_ema50 and latest_ema50 > latest_ema200:
        bias = 'Bullish'
    elif latest_close < latest_ema50 and latest_ema50 < latest_ema200:
        bias = 'Bearish'
    else:
        bias = 'Neutral'

    return latest_close, latest_ema50, latest_ema200, bias

# Generate Email Content
def generate_email_content():
    api_key = os.getenv('news_api_key')

    # List of stocks to fetch news for
    watchlist = ["AAPL", "TSLA", "GOOG"]
    watchlist_news = ""

    # Generate Watchlist News
    for stock in watchlist:
        news = fetch_news(stock, api_key)
        watchlist_news += f"<h3>{stock} News:</h3><ul>{news}</ul>"

    # Add Market Bias Analysis for S&P 500 (VUSA)
    ticker = 'VUSA.L'
    latest_close, latest_ema50, latest_ema200, bias = calculate_market_bias(ticker)
    market_summary = f"""
    <h3>Market Bias for {ticker}:</h3>
    <p>Latest Close: {latest_close}</p>
    <p>50-day EMA: {latest_ema50}</p>
    <p>200-day EMA: {latest_ema200}</p>
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
    to_email = 'nylewagjiani@gmail.com'
    password = os.getenv('password')

    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
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
