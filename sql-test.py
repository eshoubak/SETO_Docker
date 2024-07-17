###Test program to check psql server
import psycopg2

# Define our connection string
conn_string = "host='192.168.1.90' port='5488' dbname='my_data_wh_db' user='my_data_wh_user' password='my_data_wh_pwd'"

# Get a connection, if a connect cannot be made an exception will beraised here
conn = psycopg2.connect(conn_string)

# conn.cursor will return a cursor object, you can use this cursor toperform queries
cursor = conn.cursor()

# Execute a command: this creates a new table
cursor.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

# Insert some test data
cursor.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "testdata"))

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cursor.close()
conn.close()

