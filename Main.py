import os
import smtplib
from email.mime.text import MIMEText
import yfinance as yf
import requests


# Fetch News Headlines
def fetch_news(stock_symbol, api_key):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={api_key}"
    response = requests.get(url)
    articles = response.json().get("articles", [])

    headlines = []
    for article in articles[:3]:  # Get top 3 headlines
        headlines.append(f"<li><a href='{article['url']}'>{article['title']}</a></li>")
    return "\n".join(headlines)


# Generate Email Content
def generate_email_content():
    api_key = os.getenv("news_api_key")

    watchlist = ["AAPL", "TSLA", "GOOG"]

    # Generate Watchlist News
    watchlist_news = ""
    for stock in watchlist:
        news = fetch_news(stock, api_key)
        watchlist_news += f"<h3>{stock} News:</h3><ul>{news}</ul>"

    # Create Email HTML
    email_body = f"""
<html>
<head>
  <style>
    body {{
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #1c1c1e;
      color: #f4f4f9;
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }}
    a {{
    color: white;
    text-decoration: none;
    }}
    .container {{
      text-align: center;
      background-color: #333;
      padding: 30px;
      border-radius: 10px;
      width: 80%;
      max-width: 800px;
    }}
    h1 {{
      color: #ff6347;
      font-size: 3rem;
      margin-bottom: 20px;
    }}
    h2 {{
      color: #32cd32;
      font-size: 2rem;
      margin-bottom: 10px;
    }}
    h3 {{
      color: #0073e6;
      font-size: 1.5rem;
    }}
    .watchlist {{
      margin-top: 20px;
      padding: 15px;
      background-color: #444;
      border-radius: 8px;
      text-align: left;
    }}
    .watchlist p {{
      font-size: 1.2rem;
      color: #fff;
      margin: 10px 0;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 0.9rem;
      color: #888;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Daily Market Summary</h1>
    <h2>Watchlist News:</h2>
    <div class="watchlist">
      {watchlist_news}
    </div>
    <div class="footer">
      <p>&copy; 2025 Market Watch. All rights reserved.</p>
    </div>
  </div>
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
