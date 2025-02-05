import os
import smtplib
from email.mime.text import MIMEText
import yfinance as yf
import requests


# Fetch News Headlines
def FetchNews(StockSymbol, ApiKey):
    try:
        Url = f"https://newsapi.org/v2/everything?q={StockSymbol}&apiKey={ApiKey}"
        Response = requests.get(Url)
        Response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

        Articles = Response.json().get("articles", [])
        Headlines = [
            Article["title"] for Article in Articles[:3]
        ]  # Extract titles of top 3 articles

        return Headlines
    except requests.exceptions.RequestException as E:
        print(f"Error fetching news: {E}")
        return []


# Get Stock Analysis
def GetStockAnalysis(StockSymbol):
    try:
        Stock = yf.Ticker(StockSymbol)
        Recommendations = Stock.recommendations
        
        if Recommendations is not None and not Recommendations.empty:
            LatestRec = Recommendations.iloc[-1]['To Grade']
            return LatestRec
        return "No Analysis Available"
    except Exception as E:
        print(f"Error fetching analysis for {StockSymbol}: {E}")
        return "Analysis Error"


# Generate Email Content
def GenerateEmailContent():
    ApiKey = os.getenv("NEWS_API_KEY")

    # List of stocks to fetch news for
    Watchlist = ["AAPL", "AMZN", "FB", "GOOG", "NFLX", "TSLA", "NVDA"]

    WatchlistNews = ""

    # Generate Watchlist News
    for Stock in Watchlist:
        News = FetchNews(Stock, ApiKey)
        Analysis = GetStockAnalysis(Stock)

        WatchlistNews += f"""
            <h3>{Stock} - Analyst Rating: <span style="color: #00ff00">{Analysis}</span></h3>
            <ul>{' '.join([f'<li>{Headline}</li>' for Headline in News])}</ul>
        """

    # Create Email HTML
    EmailBody = f"""
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
            {WatchlistNews}
        </div>
    </body>
    </html>
    """

    return EmailBody


Email = os.getenv("EMAIL")


# Send Email
def SendEmail(Subject, Body):
    FromEmail = os.getenv("EMAIL")
    ToEmail = FromEmail  # You can adjust this if you want to send it to others
    Password = os.getenv("PASSWORD")

    Msg = MIMEText(Body, "html")
    Msg["Subject"] = Subject
    Msg["From"] = FromEmail
    Msg["To"] = ToEmail

    # Mark email as important
    Msg["X-Priority"] = "1"  # '1' is the highest priority (important)

    with smtplib.SMTP("smtp.gmail.com", 587) as Server:
        Server.starttls()
        Server.login(FromEmail, Password)
        Server.sendmail(FromEmail, ToEmail, Msg.as_string())


# Main Function
def Main():
    # Generate email content
    EmailBody = GenerateEmailContent()

    # Send the email
    SendEmail("Daily Market Summary", EmailBody)


if __name__ == "__main__":
    Main()
