import os
import re
import praw
from dotenv import load_dotenv

load_dotenv()
reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT"),
    username=os.environ.get("REDDIT_USERNAME"),
    password=os.environ.get("REDDIT_PASSWORD")
)


def handle_mention():
    for mention in reddit.inbox.mentions():
        print(mention.new)
        if (mention.new):
            mention.reply('Testing123')


def get_stock_price(stock):
    pass


def buy_stock(stock):
    pass


def sell_stock(stock):
    pass


if __name__ == "__main__":
    handle_mention()
