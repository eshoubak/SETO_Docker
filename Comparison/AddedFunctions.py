#Additional functions to use in the main code
import psycopg2 as pg
import pandas as pd
from sqlalchemy import create_engine
import os
import time
from io import StringIO

def uploadTransversionFiles(host_address, username, password, port, db_name):
    #Upload the files for the transversion of OpenDSS to Matlab and vice versa
    #The files are stored in the same folder
    #Take care of the order of the files as they are hardcoded
    
    print("Uploading transversion files")
    success = False
    trys = 0
    while not success:
        try:
            engine = create_engine('postgresql://'+username+':'+password+'@'+host_address+':'+port+'/'+db_name)
            #print("Working directory:", os.getcwd())
            df = pd.read_csv('DER_Bus_Data.csv')
            df.to_sql('busname_busnumber', engine, if_exists='replace')
            df = pd.read_csv('Loadinfo.csv')
            df.to_sql('loadname_busname', engine, if_exists='replace')
            print("Successfully uploaded transversion files!\n")
            success = True
        except:
            trys += 1
            if trys % 10 == 0:
                print("Could not connect to the database. Retrying...")
            time.sleep(1)
            continue

def initializeResultsTable(cursor, table_name):
    #Create the table for the results
    cursor.execute("CREATE TABLE " + table_name + " (BusName INT, LoadName TEXT, BusNumber INT, Time INT, TimeStep INT, TrackingStep INT, Phase TEXT, Type INT, P_matlab FLOAT, Q_matlab FLOAT, P_opendss FLOAT, Q_opendss FLOAT, P_delta FLOAT, Q_delta FLOAT)")
    print("Table " + table_name + " created successfully!\n")

def connectToDatabase(host_address, username, password, port, db_name):
    #Connect to the database
    conn_string = ("host=" + host_address + " port=" + port + " dbname=" + db_name + " user=" + username + " password=" + password)
    print("Connecting to database\n	->%s" % (conn_string))
    success = False
    while not success:
        try:
            conn = pg.connect(conn_string)
            cursor = conn.cursor()
            print("Connection successfull!\n")
            success = True
        except:
            print("Could not connect to the database. Retrying...")
            time.sleep(1)
            continue
    return conn, cursor

def fetchTable(cursor, table_name):
    #Fetch the table from the database
    cursor.execute("SELECT * FROM " + table_name)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    return df

def uploadDataframes(cursor, df, table_name):
    #Upload the dataframe to the database
    sio = StringIO()
    sio.write(df.to_csv(index=None, header=None))  # Write the Pandas DataFrame as a csv to the buffer
    sio.seek(0)
    cursor.copy_from(sio, table_name, columns=df.columns, sep=',')
    
    #output = StringIO()
    #df.to_csv(output, sep='\t', header=False, index=False)
    #output.seek(0)
    #cursor.copy_from(output, table_name, null="")
    print("Data uploaded to table " + table_name + " successfully!\n")