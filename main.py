import mysql.connector
import os
from dotenv import load_dotenv
import praw
import time
from Controllers.Stock import Stock
from Controllers.Reddit import Reddit
load_dotenv()

mydb = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    passwd=os.environ.get("DB_PASSWD"),
    database=os.environ.get("DB_NAME")
)

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT"),
    username=os.environ.get("REDDIT_USERNAME"),
    password=os.environ.get("REDDIT_PASSWORD")
)


if __name__ == "__main__":
    cursor = mydb.cursor()
    stock = Stock(mydb, cursor)
    reddit_class = Reddit(stock, reddit, cursor)
    while True:
        reddit_class.handle_mention()
        # TODO: CLEAN THIS UP TO CHECK IF THIS NEEDS TO BE DONE
        # (NO NEW MENTIONS)
        keepalive = "Select * FROM stocks"
        cursor.execute(keepalive)
        result = cursor.fetchall()
        print("Keeping SQL connection alive")
        time.sleep(20)
    cursor.close()
    mydb.close()

    pass
