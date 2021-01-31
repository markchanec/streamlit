#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import mysql.connector
import random

#constants used apart from column names
#any function, variables with 0 or 1 suffix are to be used in conjunction
SCHEMA = "Axie"
TABLENAMES = ["IQR", "KDE"]
CSV0 = "csv/final_output_valuation_quantiles.csv"
CSV1 = "csv/final_output_valuation_all.csv"


# In[2]:


def connect_DB():
    try :  
        cn = mysql.connector.connect(host = 'localhost',
                                     user = "root",
                                     passwd = "abcd",
                                     port = 3306,
                                     auth_plugin = 'mysql_native_password',
                                     use_pure = True )
        db = cn.cursor(buffered=True)
        print("Server connected successfully")
        return db, cn
    except Exception as err:
        print("DB error:", err)
        return None


# In[3]:


def create_schema(db, schema):
    try :
        db.execute('''DROP DATABASE IF EXISTS {}'''.format(schema))
        db.execute('''CREATE DATABASE {}'''.format(schema))
        print("Success! New DB -", schema, "is created")
    except Exception as err:
        print("DB error:", err)


# In[4]:


def connect_schema(db, schema):
    try:
        db.execute('''USE {}'''.format(schema))
        print(schema, "connected successfully")
    except Exception as err:
        print("DB error:", err)


# In[5]:


def create_table0(db, tablename):
    create_table_sql = '''CREATE TABLE {} ( 
    token_ids INT UNSIGNED NOT NULL PRIMARY KEY,
    mean_valuation DOUBLE UNSIGNED NOT NULL,
    median_valuation DOUBLE UNSIGNED NOT NULL,
    Q05_valuation DOUBLE UNSIGNED NOT NULL,
    Q95_valuation DOUBLE UNSIGNED NOT NULL
    )'''.format(tablename)

    try:
        db.execute('DROP TABLE if exists {}'.format(tablename))
        db.execute(create_table_sql)
        print(tablename, "table created")
    except Exception as err:
        print("DB error:", err)


# In[6]:


def insertRow0(db, cn, tablename, data):
    add = '''INSERT INTO {} 
    ( token_ids, mean_valuation, median_valuation, Q05_valuation, Q95_valuation ) 
    VALUES (%s, %s, %s, %s, %s)'''.format(tablename)
    try:
        db.execute(add, data)
        cn.commit()
        return True;
    except mysql.connector.Error as InsertError:
        print("Failed to insert record into MySQL table: {}".format(InsertError))
        return False;
    except Exception as err:
        print("Server error:", err)
        return False;


# In[7]:


def create_table1(db, tablename):
    sql_head = "CREATE TABLE " + tablename + " ( token_ids INT UNSIGNED NOT NULL PRIMARY KEY,"
    sql_tail = "X100 DOUBLE UNSIGNED NOT NULL)"
    sql_body = ""
    for i in range(1, 100): #1 to 99
        sql_body += "X" + str(i) + " DOUBLE UNSIGNED NOT NULL,"
    
    create_table_sql = sql_head + sql_body + sql_tail

    try:
        db.execute('DROP TABLE if exists {}'.format(tablename))
        db.execute(create_table_sql)
        print(tablename, "table created")
    except Exception as err:
        print("DB error:", err)


# In[8]:


def insertRow1(db, cn, tablename, data):
    sql_head = "INSERT INTO " + tablename + " ( token_ids,"
    
    column_names = ""
    for i in range(1, 100): #x1 to x99
        column_names += "X" + str(i) + ","
        
    sql_mid = "X100) VALUES ("
    
    values = ""
    for i in range(0, 100): #tokenID, x1 to x99
        values += "%s,"
    
    add = sql_head+column_names+sql_mid+values+"%s)"
    
    try:
        db.execute(add, data)
        cn.commit()
        return True;
    except mysql.connector.Error as InsertError:
        print("Failed to insert record into MySQL table: {}".format(InsertError))
        return False;
    except Exception as err:
        print("Server error:", err)
        return False;


# In[9]:


def test_service(abc):
    return abc


# In[10]:


def init_webapp(id):
    db, cn = connect_DB()
    connect_schema(db, SCHEMA)
    
    Iqr = None
    Kde = None
        
    try:
        db.execute('SELECT Q05_valuation, Q95_valuation FROM {} WHERE token_ids={}'.format(TABLENAMES[0], id))
        Iqr = db.fetchone()
        
        column_names = ""
        for i in range(1, 100): #x1 to x99
            column_names += "X" + str(i) + ","
        column_names += "X100"
        db.execute('SELECT {} FROM {} WHERE token_ids={}'.format(column_names, TABLENAMES[1], id))
        Kde = db.fetchone()
    except Exception as err:
        print("DB error:", err)

    db.close()
    cn.close()
    return Iqr,Kde


# In[11]:


def getRecord(id):
    init_webapp(id)


# In[12]:


def getRandomID():
    db, cn = connect_DB()
    connect_schema(db, SCHEMA)
    
    try:
        db.execute('SELECT * FROM {}'.format(TABLENAMES[0]))
        randomRow = random.randint(1, db.rowcount)
        print("randomRow =", randomRow)
        db.execute('SELECT token_ids FROM {} LIMIT {},1'.format(TABLENAMES[0], randomRow-1))
        randomID = db.fetchone()
    except Exception as err:
        print("DB error:", err)
        randomID = None

    db.close()
    cn.close()
    return randomID


# In[13]:


def main():    #read csv and convert into mysql
    db, cn = connect_DB()
    create_schema(db, SCHEMA)
    connect_schema(db, SCHEMA)
    
    
    #unlimit this for production copy
    df = pd.read_csv(CSV0, nrows=90000)
    print("CSV0 size =", df.shape)
    
    create_table0(db, TABLENAMES[0])
    count = 0
    #use jupyter notebook --NotebookApp.iopub_data_rate_limit=1.0e10
    #if IOPub data rate exceeded in notebook
    DATA = df.values.tolist()
    for x in DATA:
        if insertRow0(db, cn, TABLENAMES[0], x ):
            count += 1
        print("{} row(s) inserted successfully".format(count), end='\r')
    print("{} row(s) inserted successfully".format(count))
    
    
    #unlimit this for production copy
    df = pd.read_csv(CSV1, nrows=90000)
    print("CSV1 size =", df.shape)
    
    create_table1(db, TABLENAMES[1])
    count = 0
    DATA = df.values.tolist()
    for x in DATA:
        if insertRow1(db, cn, TABLENAMES[1], x ):
            count += 1
        print("{} row(s) inserted successfully".format(count), end='\r')
    print("{} row(s) inserted successfully".format(count))
    
    
    
    #close cursor and connection
    db.close()
    cn.close()
    print("Database and server connection closed")


# In[14]:


if __name__ == "__main__":
    main()

