### Author: Bodo Baumann
### github: github.com/sarkspasst
### Organization: UNC Charlotte EPIC
### Date: 06/10/2024

import psycopg2 as pg
import pandas as pd
import numpy as np
import AddedFunctions as af

### Set up databases
# Connection variables
host_address ="192.168.1.90"
username = "seto_db_user"
password = "seto_db_pwd"
port = "5488"

#Upload the files for the transversion of OpenDSS to Matlab and vice versa
af.uploadTransversionFiles(host_address, username, password, port, "setomatlabdb")
# Connect to the databases
conn_matlab, cursor_matlab = af.connectToDatabase(host_address, username, password, port, "setomatlabdb")
conn_opendss, cursor_opendss = af.connectToDatabase(host_address, username, password, port, "setoopendsdb")
conn_comparison, cursor_comparison = af.connectToDatabase(host_address, username, password, port, "setocomparisondb")

### Fetch tables
df_matlab = af.fetchTable(cursor_matlab, "result_all")
df_opendss = af.fetchTable(cursor_opendss, "opendssdata")
df_loadname_busname = af.fetchTable(cursor_comparison, "loadname_busname")
df_busname_busnumber = af.fetchTable(cursor_comparison, "busname_busnumber")

