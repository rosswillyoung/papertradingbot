from dotenv import load_dotenv
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import mydb


load_dotenv()

stock_url = os.environ.get("STOCK_URL")

cursor = mydb.cursor()

def get_stock_price(stock):
    r = requests.get(stock_url + stock)
    price = r.json()[0]['askPrice']
    return price


def buy_stock(user, stock_symbol, quantity):
    get_or_create_user(user)
    # CHECK IF USER HAS THE MONEY
    r = requests.get(stock_url + stock_symbol)
    price = r.json()[0]['askPrice']
    money_needed = price * quantity
    money_after_buying = get_users_money(user) - money_needed
    if (money_after_buying < 0):
        print(user + ' does not have enough moneys')
    # SUBTRACT QUANTITY x STOCK PRICE FROM USERS MONEY
    else:
        add_stock(stock_symbol)
        sql = "UPDATE users SET money = %s WHERE username = %s"
        values = (money_after_buying,user)
        cursor.execute(sql, values)
        mydb.commit()
        # ADD STOCK & QUANTITY TO SQL TABLE
        if check_user_stock(user, stock_symbol):
            updated_quantity = quantity + get_user_stock_quantity(user, stock_symbol)
            sql = "UPDATE user_stocks SET quantity = %s WHERE user_id = %s AND stock_id = %s"
            values = (updated_quantity, get_user_id(user), get_stock_id(stock_symbol))
            cursor.execute(sql, values)
            mydb.commit()
        else:
            sql = "INSERT INTO user_stocks (user_id, stock_id, quantity) VALUES (%s, %s, %s)"
            values = (get_user_id(user), get_stock_id(stock_symbol), quantity)
            cursor.execute(sql, values)
            mydb.commit()

    pass


def sell_stock(user, stock_symbol, quantity):
    # CHECK IF THEY HAVE THE QUANTITY
    # sql = "SELECT quantity FROM user_stocks WHERE user_id = %s AND stock_id = %s"
    # user_id = get_user_id(user)
    # stock_id = get_stock_id(stock_symbol)
    # values = (user_id, stock_id)
    # cursor.execute(sql, values)
    # result = cursor.fetchall()
    # owned_quantity = 0
    # for i in result:
    #     owned_quantity += i[0] 
    owned_quantity = get_user_stock_quantity(user, stock_symbol)
    print(owned_quantity)
    if owned_quantity < quantity:
        print(user + ' does not own that many')
    # ADD QUANTITY x STOCK PRICE TO USERS MONEY
    else:
        r = requests.get(stock_url + stock_symbol)
        price_per_share = r.json()[0]['askPrice']
        total_price = price_per_share * quantity
        updated_money = get_users_money(user) + total_price
        print(total_price)
        sql = "UPDATE users SET money = %s WHERE username = %s"
        values = (updated_money, user)
        cursor.execute(sql, values)
        print(user + ' now has ' + str(updated_money) + ' moneys')
        mydb.commit()
    # UPDATE QUANTITY TO SQL TABLE
        sql = "UPDATE user_stocks SET quantity = %s WHERE user_id = %s AND stock_id = %s"
        new_quantity = owned_quantity - quantity
        values = (new_quantity, user_id, stock_id)
        cursor.execute(sql, values)
        mydb.commit()
    pass

def get_user_id(user):
    sql = "SELECT user_id FROM users WHERE username = %s"
    values = (user,)
    cursor.execute(sql, values)
    result = cursor.fetchall()[0][0]
    return result

def get_stock_id(stock_symbol):
    sql = "SELECT stock_id FROM stocks WHERE stock_symbol = %s"
    values = (stock_symbol,)
    cursor.execute(sql, values)
    try:
        result = cursor.fetchall()[0][0]
        return result
    except IndexError:
        print("stock not in table")
        return None

def get_users_money(user):
    sql = "SELECT money FROM users WHERE username=%s"
    values = (user,)
    cursor.execute(sql, values)
    result = cursor.fetchall()[0][0]
    print(user + ' has ' + str(result) + ' moneys')
    return result


def get_or_create_user(username):
    sql = "SELECT username FROM users WHERE username=%s"
    values = (username,)
    cursor.execute(sql, values)
    result = cursor.fetchall()
    if len(result) > 0:
        print('username already exists')
        return result
    else:
        sql = "INSERT INTO users (username, money) VALUES (%s, %s)"
        values = (username, 1000000)
        cursor.execute(sql, values)
        mydb.commit()


def add_stock(stock_symbol):
    # CHECK IF STOCK ALREADY IN TABLE
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
        except IndexError:
            print('stock does not exist')
    pass

def check_user_stock(user, stock_symbol):
    user_id = get_user_id(user)
    stock_id = get_stock_id(stock_symbol)
    sql = "SELECT * FROM user_stocks WHERE stock_id = %s AND user_id = %s"
    values = (stock_id, user_id)
    cursor.execute(sql, values)
    result = cursor.fetchall()
    if len(result) > 0:
        return True
    else:
        return False
        
def get_user_stock_quantity(user, stock_symbol):
    user_id = get_user_id(user)
    stock_id = get_stock_id(stock_symbol)
    sql = "SELECT quantity FROM user_stocks WHERE stock_id = %s AND user_id = %s"
    values = (stock_id, user_id)
    cursor.execute(sql, values)
    result = cursor.fetchall()[0][0]
    return result


if __name__ == "__main__":
    cursor = mydb.cursor()
    # print(check_user_stock('jahum', 'TSLA'))
    # sell_stock('jahum', 'TSLA', 20)
    # buy_stock('jahum', 'TSLA', 10)
    # print(get_user_stock_quantity('jahum', 'TSLA'))
    get_or_create_user('Rosswilly')
    # print(get_user_id('jahum'))
    # print(get_stock_id('FB'))
    # add_stock('FB')
    # get_users_money('jahum')
    # print(get_stock_price('AAPL'))
    # handle_mention()
    cursor.close()
    mydb.close()
