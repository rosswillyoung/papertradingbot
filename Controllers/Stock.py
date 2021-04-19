from dotenv import load_dotenv
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from main import mydb

load_dotenv()

class Stock:
    def __init__(self, mydb, cursor):
        self.cursor = cursor 
        self.mydb = mydb
        self.stock_url = os.environ.get("STOCK_URL")


    def get_stock_price(self, stock):
        r = requests.get(self.stock_url + stock)
        price = r.json()[0]['askPrice']
        return price


    def buy_stock(self, user, stock_symbol, quantity):
        self.get_or_create_user(user)
        # CHECK IF USER HAS THE MONEY
        r = requests.get(self.stock_url + stock_symbol)
        price = r.json()[0]['askPrice']
        money_needed = price * quantity
        money_after_buying = self.get_users_money(user) - money_needed
        if (money_after_buying < 0):
            print(user + ' does not have enough moneys')
        # SUBTRACT QUANTITY x STOCK PRICE FROM USERS MONEY
        else:
            self.add_stock(stock_symbol)
            sql = "UPDATE users SET money = %s WHERE username = %s"
            values = (money_after_buying,user)
            self.cursor.execute(sql, values)
            self.mydb.commit()
            # ADD STOCK & QUANTITY TO SQL TABLE
            if self.check_user_stock(user, stock_symbol):
                updated_quantity = quantity + self.get_user_stock_quantity(user, stock_symbol)
                sql = "UPDATE user_stocks SET quantity = %s WHERE user_id = %s AND stock_id = %s"
                values = (updated_quantity, self.get_user_id(user), self.get_stock_id(stock_symbol))
                self.cursor.execute(sql, values)
                self.mydb.commit()
            else:
                sql = "INSERT INTO user_stocks (user_id, stock_id, quantity) VALUES (%s, %s, %s)"
                values = (self.get_user_id(user), self.get_stock_id(stock_symbol), quantity)
                self.cursor.execute(sql, values)
                self.mydb.commit()

        pass


    def sell_stock(self, user, stock_symbol, quantity):
        owned_quantity = self.get_user_stock_quantity(user, stock_symbol)
        # print(owned_quantity)
        if owned_quantity < quantity:
            print(user + ' does not own that many')
        # ADD QUANTITY x STOCK PRICE TO USERS MONEY
        else:
            r = requests.get(self.stock_url + stock_symbol)
            price_per_share = r.json()[0]['askPrice']
            total_price = price_per_share * quantity
            updated_money = self.get_users_money(user) + total_price
            print(total_price)
            sql = "UPDATE users SET money = %s WHERE username = %s"
            values = (updated_money, user)
            self.cursor.execute(sql, values)
            print(user + ' now has ' + str(updated_money) + ' moneys')
            self.mydb.commit()
        # UPDATE QUANTITY TO SQL TABLE
            sql = "UPDATE user_stocks SET quantity = %s WHERE user_id = %s AND stock_id = %s"
            new_quantity = owned_quantity - quantity
            values = (new_quantity, self.get_user_id(user), self.get_stock_id(stock_symbol))
            self.cursor.execute(sql, values)
            self.mydb.commit()
        pass

    def get_user_id(self, user):
        sql = "SELECT user_id FROM users WHERE username = %s"
        values = (user,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()[0][0]
        return result

    def get_stock_id(self, stock_symbol):
        sql = "SELECT stock_id FROM stocks WHERE stock_symbol = %s"
        values = (stock_symbol,)
        self.cursor.execute(sql, values)
        try:
            result = self.cursor.fetchall()[0][0]
            return result
        except IndexError:
            print("stock not in table")
            return None

    def get_users_money(self, user):
        sql = "SELECT money FROM users WHERE username=%s"
        values = (user,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()[0][0]
        print(user + ' has ' + str(result) + ' moneys')
        return result


    def get_or_create_user(self, username):
        sql = "SELECT username FROM users WHERE username=%s"
        values = (username,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()
        if len(result) > 0:
            print('username already exists')
            return result
        else:
            sql = "INSERT INTO users (username, money) VALUES (%s, %s)"
            values = (username, 1000000)
            self.cursor.execute(sql, values)
            self.mydb.commit()


    def add_stock(self, stock_symbol):
        # CHECK IF STOCK ALREADY IN TABLE
        sql = "SELECT stock_symbol FROM stocks WHERE stock_symbol=%s"
        values = (stock_symbol,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()
        if len(result) > 0:
            print('stock already in table')
        else:
            # CHECK IF STOCK EXISTS IN IEX
            r = requests.get(self.stock_url + stock_symbol)
            try:
                response = r.json()[0]
                print(response)
                sql = "INSERT INTO stocks (stock_symbol) VALUES (%s)"
                values = (stock_symbol,)
                self.cursor.execute(sql, values)
                self.mydb.commit()
            except IndexError:
                print('stock does not exist')
        pass

    def check_user_stock(self, user, stock_symbol):
        user_id = self.get_user_id(user)
        stock_id = self.get_stock_id(stock_symbol)
        sql = "SELECT * FROM user_stocks WHERE stock_id = %s AND user_id = %s"
        values = (stock_id, user_id)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()
        if len(result) > 0:
            return True
        else:
            return False
            
    def get_user_stock_quantity(self, user, stock_symbol):
        user_id = self.get_user_id(user)
        stock_id = self.get_stock_id(stock_symbol)
        sql = "SELECT quantity FROM user_stocks WHERE stock_id = %s AND user_id = %s"
        values = (stock_id, user_id)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()[0][0]
        return result

    def get_all_stocks_from_user(self, user):
        user_id = self.get_user_id(user)
        sql = "SELECT * FROM user_stocks WHERE user_id = %s"
        values = (user_id,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()
        stocks = {}
        for i in result:
            stocks[self.get_stock_symbol(i[2])] = i[3]
        # print(stocks)
        return stocks 

    def get_stock_symbol(self, stock_id):
        sql = "SELECT stock_symbol FROM stocks WHERE stock_id = %s"
        values = (stock_id,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()[0][0]
        return result

    def get_stock_value(self, stock_symbol, quantity):
        r = requests.get(self.stock_url + stock_symbol)
        price = r.json()[0]['askPrice']
        result = price * quantity
        # print(result)
        return result

    def get_total_stock_value(self, stock_dict):
        result = 0
        for i in stock_dict:
            result += self.get_stock_value(i, stock_dict[i])
        # print(result)
        return result

if __name__ == "__main__":
    stocks = Stock(mydb.cursor())
    print(stocks.get_total_stock_value(stocks.get_all_stocks_from_user('jahum')))
    mydb.close()
