import os
import smtplib
from email.mime.text import MIMEText
import yfinance as yf
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Fetch News Headlines
def fetch_news(stock_symbol, api_key):
    try:
        url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        
        articles = response.json().get("articles", [])
        headlines = [article['title'] for article in articles[:3]]  # Extract titles of top 3 articles
        
        return headlines
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []


# Sentiment Analysis to predict stock movement
def analyze_sentiment(headlines):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = []

    for headline in headlines:
        sentiment_score = analyzer.polarity_scores(headline)
        sentiment_scores.append(sentiment_score['compound'])  # 'compound' gives the overall sentiment score

    # If average sentiment score is positive, predict up, otherwise down
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    return "Up" if avg_sentiment > 0 else "Down"

# Calculate market bias based on today's price action
def calculate_market_bias(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1d")
        
        if data.empty:
            print(f"No data returned for {ticker}")
            return None, None, "No Data"
        
        today_open = data['Open'].iloc[0]
        yesterday_close = data['Close'].iloc[0]
        
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
    api_key = os.getenv("NEWS_API_KEY")

    # List of stocks to fetch news for
    watchlist = ["AAPL", "TSLA", "GOOG"]
    watchlist_news = ""

    # Generate Watchlist News and sentiment prediction
    for stock in watchlist:
        news = fetch_news(stock, api_key)
        predicted_movement = analyze_sentiment(news)  # Use the 'news' directly here
        watchlist_news += f"<h3>{stock} News:</h3><ul>{' '.join([f'<li>{headline}</li>' for headline in news])}</ul><p>Predicted Movement: {predicted_movement}</p>"

    # Add Market Bias Analysis for S&P 500 (VUSA)
    ticker = "VUSA.L"
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

email = os.getenv("EMAIL")
# Send Email
def send_email(subject, body):
    from_email = email
    to_email = email
    password = os.getenv("PASSWORD")

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
