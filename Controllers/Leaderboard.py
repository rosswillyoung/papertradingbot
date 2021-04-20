from Stock import Stock
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

mydb = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    passwd=os.environ.get("DB_PASSWD"),
    database=os.environ.get("DB_NAME")
)

def get_usernames_and_money(cursor):
    sql = "SELECT username, money FROM users"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def user_in_leaderboard(cursor, username):
    sql = "SELECT username FROM Leaderboard WHERE username = %s"
    values = (username,)
    cursor.execute(sql, values)
    result = cursor.fetchall()
    if cursor.rowcount == 0:
        return False
    else:
        return True


if __name__ == '__main__':
    # RUN THIS ONCE A DAY TO UPDATE LEADERBOARD?
    cursor = mydb.cursor()
    stock = Stock(mydb, cursor)
    for i in get_usernames_and_money(cursor):
        username = i[0]
        money = float(i[1])
        all_stocks = stock.get_all_stocks_from_user(username)
        total_stock_value = float(stock.get_total_stock_value(all_stocks))
        total_value = money + total_stock_value
        if user_in_leaderboard(cursor, username):
            sql = "UPDATE Leaderboard SET total_value = %s WHERE username = %s"
            values = (total_value, username)
            cursor.execute(sql, values)
        else:
            sql = "INSERT INTO Leaderboard(username, total_value) VALUES (%s, %s)"
            values = (username, total_value)
            cursor.execute(sql, values)
        mydb.commit()

    cursor.close()
    mydb.close()