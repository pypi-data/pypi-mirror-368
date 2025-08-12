"""
https://hackingandslacking.com/connecting-pandas-to-a-database-with-sqlalchemy-b6a187675c4a
https://www.youtube.com/watch?v=qw--VYLpxG4 (full course)
https://aws.amazon.com/blogs/database/managing-postgresql-users-and-roles/ (user management)
"""

import pandas as pd
from sqlalchemy import create_engine

db_host = "postgres-one.cfor89dvxtd9.eu-central-1.rds.amazonaws.com"
db_name = "postgres"
db_user = "ben"
db_pass = "3xm8RhALw3gvmf8hByQK"

try:
    engine = create_engine(
        ("postgresql://" + db_user + ":" + db_pass + "@" + db_host + "/" + db_name)
    )
    print("connection")
    engine.execute("set schema '{}'".format("public"))
    print(engine.table_names())
except:
    print("failed to get connection")


# create
df = pd.DataFrame({"a": [1, 2, 3, 4, 5, 6], "b": [1, 2, 3, 4, 5, 6]})
print(df)

# upload
df.to_sql("users", con=engine, if_exists="replace")


# get data
print(pd.read_sql("select a,b from users where a in (1,2);", engine))

table = "users"
engine.execute("drop table {};".format(str(table)))

# print current database and schema
print(engine.execute("SELECT current_database();").fetchall())
print(engine.execute("SELECT current_schema();").fetchall())

# create and drop schema
engine.execute("create schema ben;")  # create and move to?
engine.execute("drop schema ben;")

engine.dispose()
