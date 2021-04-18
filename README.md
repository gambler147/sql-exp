# sql-exp
Experiments on sql commands. This program is an experiment for comparing the speed of inserting multiple records into sql database. It creates random integers for specified size and will try to connect with database and table. Please make sure configured table and database are not important because it will drop and create the same table repeatedly.

## Config
You need to add `config.json` in current directory and specify the mysql configurations

```json
{
  "host": "yourhost",
  "database": "yourdatabase",
  "user": "username",
  "password": "password",
  "table": "yourtable",
  "port": 3306
}
```

## Run the script
run
```bash
python run.py -c [number of columns] -n [number of records]
```
you can add list of choices for columns and number of records. It will print out results for every pair of combination.

run 
```bash
python run.py -h
``` 
for detailed instructions.


## Insertion Methods
- **Execute the single insertion query multiple times**. 

  This is the naive way of inserting data to databases. The drawback might be there could be too many interactions with the database.

  for example.
  ```python
  for d in data:
    query = "INSERT INTO table VALUES (....)";
    cursor.execute(query)
  ```

- **combine multiple insertion queries to one single string query**.

  Instead of doing a inserting query and executing it for every record, construct the query string and execute the final query string once.

  for example. 
  ```python
  query = """INSERT INTO table VALUES (1,2,3);
            INSERT INTO table VALUES (4,5,6);
            ...
          """
  cursor.execute(query)
  ```

- **use single insertion query**

  We do not need to use as many 'INSERT' queries as number of records. Using one 'INSERT' is also doable.

  for example. 
  ```python
  query = """INSERT INTO table VALUES (
      (1,2,3),
      (3,3,3),
      (7,8,9)
  )
  """
  ```

- **use 'executemany' method**

  Python `mysql.connector.connect.cursor` provides `executemany` method.

  for example,
  ```python
  data = [[1,2,3], [4,5,6], [7,8,9]]
  query = """INSERT INTO table VALUES (%s, %s, %s)"""
  cursor.executemany(query, data)
  ```