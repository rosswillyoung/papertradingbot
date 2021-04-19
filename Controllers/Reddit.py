# import praw
from dotenv import load_dotenv
import os
import requests
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from main import mydb
# from stock_controller import (get_stock_price, buy_stock, sell_stock,
#                              get_users_money, get_or_create_user,
#                              get_user_stock_quantity, get_total_stock_value,
#                              get_all_stocks_from_user)

# from Stock import Stock
load_dotenv()

class Reddit:
    def __init__(self, stock, reddit):
        self.reddit = reddit
        self.stock_url = os.environ.get("STOCK_URL")
        self.stock = stock

    def handle_mention(self):
        for mention in self.reddit.inbox.mentions():
            if (mention.new):
                comment_list = mention.body.split()
                author = str(mention.author)
                footer = self.create_footer(author)
                try:
                    command = comment_list[1].lower()
                    if command == 'buy':
                        reply = self.handle_buy(author, comment_list)
                    elif command == 'sell':
                        reply = self.handle_sell(author, comment_list)
                    else:
                        reply = "Error Parsing Comment - Command Not Recognized (try 'buy' or 'sell')"
                except IndexError:
                    reply = "Error Parsing Comment - No Command Found"

                mention.reply(reply + footer)
                mention.mark_read()


    def handle_buy(self, author, comment_list):
        try:
            stock_symbol = comment_list[2]
            quantity = int(comment_list[3])
            r = requests.get(self.stock_url + stock_symbol)
            ask_price = r.json()[0]['askPrice']
            if int(ask_price) == 0:
                reply = "It looks like the stock market is closed right now and pre/post-market trading is disabled. Try again later (9:30 a.m. - 4 p.m. Eastern)"
            else:
                reply = ("u/{} just bought {} shares of {} at {} each."
                        .format(author, str(quantity), stock_symbol, ask_price))
                self.stock.buy_stock(author, stock_symbol, quantity)
            return reply
        except IndexError:
            reply = "Error Parsing Comment - Symbol or Quantity Not Found"
            return reply

    def handle_sell(self, author, comment_list):
        try:
            stock_symbol = comment_list[2]
            quantity = int(comment_list[3])
            r = requests.get(self.stock_url + stock_symbol)
            ask_price = r.json()[0]['askPrice']
            if int(ask_price) == 0:
                reply = "It looks like the stock market is closed right now and pre/post-market trading is disabled. Try again later (9:30 a.m. - 4 p.m. Eastern)"
            else:
                reply = ("u/{} just sold {} shares of {} at {} each."
                        .format(author, str(quantity), stock_symbol, ask_price))
                self.stock.sell_stock(author, stock_symbol, quantity)
            return reply
        except IndexError:
            reply = "Error Parsing Comment - Symbol or Quantity Not Found"
            return reply

    def create_footer(self, author):
        users_money = self.stock.get_users_money(str(author))
        total_stock_value = self.stock.get_total_stock_value(self.stock.get_all_stocks_from_user(str(author)))
        total_value = users_money + total_stock_value
        footer = ("\n\n\n\n\n\nu/{} has {} moneys left, and their total stock value is currently worth {}, for a total value of {}"
                        .format(author, 
                            users_money,
                            total_stock_value, 
                            total_value
                        ))
        return footer


#
#
#
#  TODO: HANDLE FORMATTING OF COMMENTS
#  MAKE IT LOOK PRETTY
#
#
#