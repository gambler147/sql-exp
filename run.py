import numpy as np
import argparse
from mysql.connector import connect, Error
import json
import time
import os

def multipleSingleInsertionLoopQuery(conn, table, data):
  """
  This is the naive way to insert data to table.
  It calls cursor.execute as many times as the number of records in data
  """
  cursor = conn.cursor()
  for d in data:
    values = "(" + ",".join(map(str, d)) + ")"
    query = "INSERT INTO {} VALUES {};".format(table, values)
    cursor.execute(query)
  conn.commit()

def multipleSingleInsertionWithOneQuery(conn, table, data):
  """
  Pack all insert query into one string and send to db to execute
  io, call cursor.execute function once
  """
  cursor = conn.cursor()
  query = []
  for d in data:
    values = "(" + ",".join(map(str, d)) + ")"
    query.append("INSERT INTO {} VALUES {};".format(table, values))
  query = ''.join(query)
  cursor.execute(query, multi=True)
  conn.commit()

def multipleInsertionWithOneQuery(conn, table, data):
  """
  Use one insert query as the following

  INSERT INTO movies (title, year, genre, collection_in_mil)
  VALUES
    ("Forrest Gump", 1994, "Drama", 330.2),
    ("3 Idiots", 2009, "Drama", 2.4),
    ("Eternal Sunshine of the Spotless Mind", 2004, "Drama", 34.5),
    ("Good Will Hunting", 1997, "Drama", 138.1),
    ("Skyfall", 2012, "Action", 304.6),
    ("Gladiator", 2000, "Action", 188.7)
  
  """
  cursor = conn.cursor()
  values = []
  for d in data:
    values.append("(" + ",".join(map(str, d)) + ")")
  values = ','.join(values)
  query = "INSERT INTO {} VALUES {}".format(table, values)
  cursor.execute(query)
  conn.commit()

def executeManyQuery(conn, table, data):
  n, c = data.shape
  """
  use cursor.executemany query

  query = INSERT INTO test VALUES (%s, %s, ...)
  cursor.executemany(query, data: list[list]) 
  """
  cursor = conn.cursor()
  values = ','.join(['%s']*c)
  query = "INSERT INTO {} VALUES ({})".format(table, values)
  cursor.executemany(query, data.tolist())
  conn.commit()

def clearTable(conn, table):
  """
  clear all current records in table
  """
  cursor = conn.cursor()
  cursor.execute("TRUNCATE TABLE {};".format(table))
  conn.commit()

def createTable(conn, table, num_cols=10, engine="INNODB"):
  """
  create table with given number of columns
  """
  cursor = conn.cursor()
  subquery = ",".join(["col" + str(i) + " INT" for i in range(1,num_cols+1)])
  query = "create table if not exists {} ({}) ENGINE={};".format(table, subquery, engine)
  cursor.execute(query)
  conn.commit()

def dropTable(conn, table):
  cursor = conn.cursor()
  cursor.execute("DROP TABLE IF EXISTS {}".format(table))
  conn.commit()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Mysql execution time comparision')
  parser.add_argument('-n', '--num', nargs = '+', type=int)
  parser.add_argument('-c', '--column', nargs = '+', type=int)
  parser.add_argument('-s', '--save_fig', nargs = '?', type=str)

  args = parser.parse_args()

  # PWD
  PWD = os.getcwd()

  # functions to test
  func_list = [
    multipleSingleInsertionLoopQuery,
    multipleSingleInsertionWithOneQuery,
    multipleInsertionWithOneQuery,
    executeManyQuery
  ]

  # database config
  with open(os.path.join(PWD, './config.json'), 'r') as f:
    config = json.load(f)
  database = config['database']
  table = config['table']
  host = config['host']
  user = config['user']
  password = config['password']
  port = config['port']

  # connect to mysql
  conn = connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=port
  )

  # main loop
  cols = args.column
  nums = args.num
  
  for c in cols:
    dropTable(conn, table)
    createTable(conn, table, num_cols=c)
    for n in nums:
      # create random integers
      data = np.random.randint(1, 1000, (n, c))
      # test all functions
      for func in func_list:
        clearTable(conn, table)
        start = time.time()
        func(conn, table, data)
        end = time.time()
        print("time elapsed for {} with {} records and {} columns: {}"
                .format(func.__name__, n, c, end-start))

  conn.close()
