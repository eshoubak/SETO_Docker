### Author: Bodo Baumann
### github: github.com/sarkspasst
### Organization: UNC Charlotte EPIC
### Date: 06/10/2024

import psycopg2 as pg
import pandas as pd
import numpy as np
import AddedFunctions as af

af.uploadTransversionFiles()

### Set up databases
# Connection variables
host_address ="192.168.1.90"
username = "seto_db_user"
password = "seto_db_pwd"
port = "5488"

# Connect to the Matlab database
db_name = "setomatlabdb"
conn_string = ("host=" + host_address + " port=" + port + " dbname=" + db_name + " user=" + username + " password=" + password)
print("Connecting to database\n	->%s" % (conn_string))
conn_matlab = pg.connect(conn_string)
cursor_matlab = conn_matlab.cursor()
print("Connected to Matlab database!\n")

# Connect to the OpenDSS database
db_name = "setoopendssdb"
conn_string = ("host=" + host_address + " port=" + port + " dbname=" + db_name + " user=" + username + " password=" + password)
print("Connecting to database\n	->%s" % (conn_string))
conn_opendss = pg.connect(conn_string)
cursor_opendss = conn_opendss.cursor()
print("Connected to OpenDSS database!\n")

# Connect to the result database
db_name = "setocomparisondb"
conn_string = ("host=" + host_address + " port=" + port + " dbname=" + db_name + " user=" + username + " password=" + password)
print("Connecting to database\n	->%s" % (conn_string))
conn_comparison = pg.connect(conn_string)
cursor_comparison = conn_comparison.cursor()
print("Connected to comparison database!\n")

### Fetch tables
# Fetch table from Matlab
cursor_matlab.execute("SELECT * FROM result_all")
rows = cursor_matlab.fetchall()
df_matlab = pd.DataFrame(rows, columns=[desc[0] for desc in cursor_matlab.description])

# Fetch table from OpenDSS
#print(cursor_opendss.execute("SELECT * FROM pg_catalog.pg_tables;"))
cursor_opendss.execute("SELECT * FROM opendssdata")
rows = cursor_opendss.fetchall()
df_opendss = pd.DataFrame(rows, columns=[desc[0] for desc in cursor_opendss.description])

# Fetch table from comparison
