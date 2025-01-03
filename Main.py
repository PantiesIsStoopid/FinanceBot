import os
import smtplib
from email.mime.text import MIMEText
import yfinance as yf
import requests
import pandas

email = os.getenv('EMAIL')

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
    api_key = os.getenv('NEWS_API_KEY')

    watchlist = ["AAPL", "TSLA", "GOOG"]
    watchlist_news = ""
  
    for stock in watchlist:
        news = fetch_news(stock, api_key)
        watchlist_news += f"<h3>{stock} News:</h3><ul>{news}</ul>"

    
    

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
    </body>
    </html>
    """

    return email_body


# Send Email
def send_email(subject, body):
    from_email = email
    to_email = email
    password = os.getenv('PASSWORD')

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
