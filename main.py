import requests
import os
from twilio.rest import Client

# Alpha Vantage auth
STOCK_NAME = "AAPL"
COMPANY_NAME = "Apple Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")

# News auth
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

# TWILIO auth
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")


# Get share prices at market closure yesterday and the day before yesterday
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": ALPHAVANTAGE_API_KEY,
}

stock_info_response = requests.get(STOCK_ENDPOINT, params=stock_params)
stock_info_data = stock_info_response.json()["Time Series (Daily)"]

stock_info_list = [value for (key, value) in stock_info_data.items()]
yesterday_data = stock_info_list[0]

yesterday_closing_price = yesterday_data["4. close"]

before_yest_data = stock_info_list[1]
before_yest_closing_price = before_yest_data["4. close"]


# Find the % difference between the above 2 prices
price_diff = (float(yesterday_closing_price) - float(before_yest_closing_price))


# Calculate % difference in price between closing price yesterday and closing price the day before yesterday
percent_diff = price_diff / float(yesterday_closing_price) * 100

up_or_down = ""

if price_diff > 0:
    up_or_down = f"🔺{round(percent_diff, 2)}%"
else:
    up_or_down = f"🔻{round(percent_diff, 2)}%"


# If % difference is greater than set value then get articles related to the company
if abs(percent_diff) > 0.5:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
        "language": "en",
        "sortBy": "popularity"
    }
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_data = news_response.json()["articles"]

    top_3_articles = [f"Headline: {article['title']}. \nBrief: {article['description']}" for article in news_data[:3]]


# Send each article as a separate message via Twilio.
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for article in top_3_articles:
        message = client.messages.create(
            body=f"{STOCK_NAME}: {up_or_down} \n{article}",
            from_="whatsapp:+14155238886",
            to="whatsapp:+17739361340",
        )
        print(message.status)

