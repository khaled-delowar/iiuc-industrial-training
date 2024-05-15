import os
import mysql.connector
from mysql.connector import Error
from db_connection import create_db_connection

cursor = connection.cursor()

# Define the ALTER TABLE statement to add a new column
alter_query = "ALTER TABLE your_table ADD COLUMN new_column_name VARCHAR(255) NOT NULL"

# Execute the ALTER TABLE statement
cursor.execute(alter_query)
