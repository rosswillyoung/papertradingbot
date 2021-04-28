from dotenv import load_dotenv
import os
import requests
load_dotenv()

class Reddit:
    def __init__(self, stock, reddit, cursor):
        self.reddit = reddit
        self.stock_url = os.environ.get("STOCK_URL")
        self.stock = stock
        self.cursor = cursor

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
                    elif command == 'leaderboard':
                        reply = self.handle_leaderboard(author, comment_list)
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

    def handle_leaderboard(self, author, comment_list):
        # GET TOP 10
        sql = "SELECT * FROM Leaderboard ORDER BY total_value DESC LIMIT 5"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        top_five = {}
        counter = 1
        for row in result:
            top_five[str(counter)] = {'user': row[1], 'money': row[2]}
            counter += 1

        reply = ("""
        |User|Money
        :--:|:--:|:--:
        {}|{}|{}
        {}|{}|{}
        {}|{}|{}
        {}|{}|{}
        {}|{}|{}
        """.format(
            '1', top_five['1']['user'], top_five['1']['money'],
            '2', top_five['2']['user'], top_five['2']['money'],
            '3', top_five['3']['user'], top_five['3']['money'],
            '4', top_five['4']['user'], top_five['4']['money'],
            '5', top_five['5']['user'], top_five['5']['money'],
            ))
        return reply

        # GET AUTHOR'S POSITION IN LEADERBOARD

        # CHECK IF ANOTHER USER MENTIONED (comment_list[2])
        # IF SO, GET THEIR POSITION IN LEADERBOARD
        pass

    def create_footer(self, author):
        user = self.stock.get_or_create_user(str(author))
        users_money = self.stock.get_users_money(str(author))
        total_stock_value = self.stock.get_total_stock_value(self.stock.get_all_stocks_from_user(str(author)))
        total_value = users_money + total_stock_value
        footer = ("\n***\nu/{} has {} moneys left, and their total stock value is currently worth {}, for a total value of {}"
                        .format(author,
                            users_money,
                            total_stock_value,
                            total_value
                        ))
        return footer


#
#
# TODO: CLEAN UP LEADERBOARD COMMENT
#
#
#
