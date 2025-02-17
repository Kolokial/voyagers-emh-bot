import sqlite3
from venv import create

def setup_database(cursor):
    schema = open("schema.sql").read()
    cursor.executescript(schema)

def createConnection():
    dbfile = 'voyagers-emh-bot.db'
    conn = None
    try:
        conn = sqlite3.Connection(dbfile, isolation_level=None)
        cursor = conn.cursor()
        setup_database(cursor)
        return cursor
    except OSError as e:
        print(e)

    return conn

def insertIntoOptOutTable(username):
    conn = createConnection()
    print('inserting')
    print(username)
    conn.execute('INSERT INTO user_optout (name) VALUES(?);',(str(username), ))
    conn.close()
    getOptoutList()

def getOptoutList():
    conn = createConnection()
    conn.execute('SELECT name FROM user_optout')
    results = conn.fetchall()
    conn.close()
    return results
