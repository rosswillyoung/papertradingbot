import re
import praw
from dotenv import load_dotenv
import requests
import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import mydb

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
        if (mention.new):
            r = requests.get(stock_url + comment_list[2])
            author = mention.author
            ask_price = r.json()[0]['askPrice']
            stock_symbol = comment_list[2]
            if comment_list[1] == "buy" or comment_list[1] == "Buy":
                mention.reply('u/{} just bought {} at {}'.format(
                    author, stock_symbol, ask_price))
            if comment_list[1] == "sell" or comment_list[1] == "Sell":
                mention.reply('u/{} just bought {} at {}'.format(
                    author, stock_symbol, ask_price))
            mention.mark_read()


def get_stock_price(stock):
    r = requests.get(stock_url + stock)
    price = r.json()[0]['askPrice']
    return price


def buy_stock(user, stock, quantity):
    # CHECK IF USER HAS THE MONEY

    # SUBTRACT QUANTITY x STOCK PRICE FROM USERS MONEY

    # ADD STOCK & QUANTITY TO SQL TABLE
    pass


def sell_stock(user, stock, quantity):
    # CHECK IF THEY HAVE THE QUANTITY

    # ADD QUANTITY x STOCK PRICE TO USERS MONEY

    # UPDATE QUANTITY TO SQL TABLE
    pass


def get_users_money(user):
    cursor = mydb.cursor()
    sql = "SELECT money FROM users WHERE username=%s"
    values = (user,)
    cursor.execute(sql, values)
    result = cursor.fetchall()[0][0]
    print(user + ' has ' + str(result) + ' moneys')
    return result


def get_or_create_user(username):
    cursor = mydb.cursor()
    sql = "SELECT username FROM users WHERE username=%s"
    values = (username,)
    cursor.execute(sql, values)
    result = cursor.fetchall()
    if len(result) > 0:
        print('username already exists')
    else:
        sql = "INSERT INTO users (username, money) VALUES (%s, %s)"
        values = (username, 1000000)
        cursor.execute(sql, values)

    mydb.commit()
    cursor.close()
    mydb.close()
    pass


def add_stock(stock_symbol):
    # CHECK IF STOCK ALREADY IN TABLE
    cursor = mydb.cursor()
    sql = "SELECT stock_symbol FROM stocks WHERE stock_symbol=%s"
    values = (stock_symbol,)
    cursor.execute(sql, values)
    result = cursor.fetchall()
    if len(result) > 0:
        print('stock already in table')
    else:
        # CHECK IF STOCK EXISTS IN IEX
        r = requests.get(stock_url + stock_symbol)
        try:
            response = r.json()[0]
            print(response)
            sql = "INSERT INTO stocks (stock_symbol) VALUES (%s)"
            values = (stock_symbol,)
            cursor.execute(sql, values)
            mydb.commit()
            cursor.close()
            mydb.close()
        except IndexError:
            print('stock does not exist')
    pass


if __name__ == "__main__":
    add_stock('FB')
    # get_users_money('jahum')
    # print(get_stock_price('AAPL'))
    # get_or_create_user('jahum')
    # handle_mention()
