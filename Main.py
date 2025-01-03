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


# Generate Email Content
def generate_email_content():
    api_key = os.getenv("NEWS_API_KEY")

    # List of stocks to fetch news for
    watchlist = ["AAPL", "AMZN", "FB", "GOOG", "NFLX", "TSLA", "NVDA"]

    watchlist_news = ""

    # Generate Watchlist News and sentiment prediction
    for stock in watchlist:
        news = fetch_news(stock, api_key)
        predicted_movement = analyze_sentiment(news)  # Use the 'news' directly here

        # Set color for sentiment prediction (green for up, red for down)
        movement_color = "green" if predicted_movement == "Up" else "red"

        watchlist_news += f"""
            <h3>{stock} News:</h3>
            <ul>{' '.join([f'<li>{headline}</li>' for headline in news])}</ul>
            <p><b style="color:{movement_color};">{predicted_movement}</b></p>
        """

    # Create Email HTML
    email_body = f"""
    <html>
    <head>
        <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #141414;
        }}
        
        .Card {{
            background-color: #141414;
            margin: 32px;
            border-radius: 30px;
            padding: 15px;
            color: white;
            text-align: center;
            border-radius: 10px;
            box-shadow: 0 0 15px 5px rgba(255, 255, 255, 0.7);  /* White glowing effect */
        }}
        
        .Title {{
            color: white;
        }}
        
        .SubtitleNews {{
            color: #0080ff;
        }}
        </style>
    </head>
    <body>
        <div class="Card">
            <h1 class="Title">Daily Market Summary</h1>
            <h2 class="SubtitleNews">Watchlist News:</h2>
            {watchlist_news}
        </div>
    </body>
    </html>
    """

    return email_body


email = os.getenv("EMAIL")

# Send Email
def send_email(subject, body):
    from_email = os.getenv("EMAIL")
    to_email = from_email  # You can adjust this if you want to send it to others
    password = os.getenv("PASSWORD")

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    
    # Mark email as important
    msg["X-Priority"] = "1"  # '1' is the highest priority (important)

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
