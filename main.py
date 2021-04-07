import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

mydb = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    passwd=os.environ.get("DB_PASSWD"),
    database=os.environ.get("DB_NAME")
)


if __name__ == "__main__":
    pass
