import mysql.connector
import os
import uuid
import time    


mysql_user = os.getenv('MYSQL_USER')
mysql_pass = os.getenv('MYSQL_PASS')
mysql_host = os.getenv('MYSQL_HOST')

cnx = mysql.connector.connect(user=mysql_user, password=mysql_pass,
                              host=mysql_host,
                              database='app')

cnx.start_transaction(isolation_level='READ COMMITTED')
cursor = cnx.cursor()

"""
USERS TABLE
"""
def login_user(email):
    query = ("select email from users where email = %s")
    cursor.execute(query, (email,))

    if len(cursor.fetchall()) == 0:
        add_user = "insert into users (email, tokens_consumed, seconds_consumed) values (%s, 0, 0)"
        cursor.execute(add_user, (email,))
        cnx.commit()

def update_tokens(email, used_tokens):
    query_tokens = ("select tokens_consumed from users where email = %s")
    cursor.execute(query_tokens, (email,))
    current_tokens = cursor.fetchall()[0][0]
    new_tokens = current_tokens + used_tokens
    query = ("update users set tokens_consumed = %s")
    cursor.execute(query, (new_tokens,))
    cnx.commit()

def get_tokens(email):
    query_tokens = ("select tokens_consumed from users where email = %s")
    cursor.execute(query_tokens, (email,))
    current_tokens = cursor.fetchall()[0][0]
    return current_tokens

def update_seconds(email, used_seconds):
    query_seconds= ("select seconds_consumed from users where email = %s")
    cursor.execute(query_seconds, (email,))
    current_sec= cursor.fetchall()[0][0]
    new_sec = current_sec + used_seconds
    query = ("update users set seconds_consumed = %s")
    cursor.execute(query, (new_sec,))
    cnx.commit()

def get_seconds(email):
    query_seconds= ("select seconds_consumed from users where email = %s")
    cursor.execute(query_seconds, (email,))
    current_sec= cursor.fetchall()[0][0]
    return current_sec

def get_purchased_seconds(email):
    query_seconds= ("select seconds_purchased from users where email = %s")
    cursor.execute(query_seconds, (email,))
    current_sec= cursor.fetchall()[0][0]
    return current_sec

def update_purchased_seconds(email, purchased_seconds):
    query_seconds = ("select seconds_purchased from users where email = %s")
    cursor.execute(query_seconds, (email,))
    current_sec = cursor.fetchall()[0][0]
    new_seconds = current_sec + purchased_seconds
    query = ("update users set seconds_purchased = %s")
    cursor.execute(query, (new_seconds,))
    cnx.commit()

"""
PAYMENTS TABLE
"""

def new_payment(email, payment_id, amount, seconds):
    update_purchased_seconds(email, seconds)
    query = ("insert into payments (id, email, date, amount) values (%s, %s, %s, %s)")
    date = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(query, (payment_id, email, date, amount))
    cnx.commit()