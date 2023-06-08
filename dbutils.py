import mysql.connector
import os


mysql_user = os.getenv('MYSQL_USER')
mysql_pass = os.getenv('MYSQL_PASS')
mysql_host = os.getenv('MYSQL_HOST')

cnx = mysql.connector.connect(user=mysql_user, password=mysql_pass,
                              host=mysql_host,
                              database='app')

cursor = cnx.cursor()

def login_user(email):
    query = ("select email from users where email = %s")
    cursor.execute(query, (email,))

    if len(cursor.fetchall()) == 0:
        add_user = "insert into users (email, tokens_consumed) values (%s, 0)"
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