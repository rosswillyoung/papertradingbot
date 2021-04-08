import praw
from dotenv import load_dotenv
import os, sys
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import mydb
from stock_controller import get_stock_price, buy_stock, sell_stock, get_users_money, get_or_create_user, get_user_stock_quantity


load_dotenv()
reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT"),
    username=os.environ.get("REDDIT_USERNAME"),
    password=os.environ.get("REDDIT_PASSWORD")
)

stock_url = os.environ.get("STOCK_URL")


def handle_mention():
    for mention in reddit.inbox.mentions():
        # print(mention.new)
        comment_list = mention.body.split()
        ###########################################################
        #
        #
        # NEED TO UPDATE WITH CHECK FOR PRE/POST MARKET
        #
        #
        #
        #############################################################
        
        if (mention.new):
            r = requests.get(stock_url + comment_list[2])
            # print(r.json())
            author = mention.author
            ask_price = r.json()[0]['askPrice']
            stock_symbol = comment_list[2]
            # print(stock_symbol)
            quantity = int(comment_list[3])
            if comment_list[1] == "buy" or comment_list[1] == "Buy":
                mention.reply('u/{} just bought {} at {}'.format(
                    author, stock_symbol, ask_price))
                buy_stock(str(author), stock_symbol, quantity)
            if comment_list[1] == "sell" or comment_list[1] == "Sell":
                mention.reply('u/{} just bought {} at {}'.format(
                    author, stock_symbol, ask_price))
            mention.mark_read()

if __name__ == "__main__":
    handle_mention()