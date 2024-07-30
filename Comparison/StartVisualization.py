### Author: Bodo Baumann
### github: github.com/sarkspasst
### Organization: UNC Charlotte EPIC
### Date: 06/10/2024

import psycopg2 as pg
import pandas as pd
import numpy as np
import AddedFunctions as af
import operator as op
import time
from io import StringIO

### Set up databases
# Connection variables
host_address ="192.168.1.90"
username = "seto_db_user"
password = "seto_db_pwd"
port = "5488"

#Upload the files for the transversion of OpenDSS to Matlab and vice versa
af.uploadTransversionFiles(host_address, username, password, port, "setocomparisondb")

# Connect to the databases
conn_matlab, cursor_matlab = af.connectToDatabase(host_address, username, password, port, "setomatlabdb")
conn_opendss, cursor_opendss = af.connectToDatabase(host_address, username, password, port, "setoopendssdb")
conn_comparison, cursor_comparison = af.connectToDatabase(host_address, username, password, port, "setocomparisondb")

# Initialize the results table
af.initializeResultsTable(cursor_comparison, "result")

### Fetch tables
#df_matlab = af.fetchTable(cursor_matlab, "result_all")
#df_opendss = af.fetchTable(cursor_opendss, "opendssdata")
df_loadname_busname = af.fetchTable(cursor_comparison, "loadname_busname")
df_busname_busnumber = af.fetchTable(cursor_comparison, "busname_busnumber")

### Set up simulation parameters
trackSteps = 4
timeSteps = 24

for i in range(1, timeSteps):
    for k in range (1, trackSteps):
        success = False
        trys = 0
        while not success:
            try:
                cursor_matlab.execute("SELECT * FROM result_all WHERE timeStep = " + str(i) + " AND trackingStep = " + str(k))
                df_matlab = pd.DataFrame(cursor_matlab.fetchall(), columns=[desc[0] for desc in cursor_matlab.description])
                cursor_opendss.execute("SELECT * FROM opendssdata WHERE timeStep = " + str(i) + " AND trackingStep = " + str(k))
                df_opendss = pd.DataFrame(cursor_opendss.fetchall(), columns=[desc[0] for desc in cursor_opendss.description])
                success = True
                print("Data loaded for time step", i, "and tracking step", k)
            except:
                trys += 1
                if trys % 10 == 0:
                    print("Could not load data for time step", i, "and tracking step", k, ". Watiting for Matlab and OpenDSS to finish the next Tracking Step.")
                time.sleep(1)
                continue
        
        # Fetch the data
        #df_matlab = pd.DataFrame(cursor_matlab.fetchall(), columns=[desc[0] for desc in cursor_matlab.description])
        #df_opendss = pd.DataFrame(cursor_opendss.fetchall())
        #print(df_opendss)

        # Build the result dataframe

        df_result = pd.DataFrame(columns=['BusName', 'LoadName', 'BusNumber', 'Time', 'TimeStep', 'TrackingStep', 'Phase', 'Type', 'P_matlab', 'Q_matlab', 'P_opendss', 'Q_opendss', 'P_delta', 'Q_delta'])
        print(df_result)
        for index, row in df_opendss.iloc[100:].iterrows():
            try:
                loadname_phase = row['busname']
                print(loadname_phase)
                phase = loadname_phase[-1]
                print(phase)
                loadname = loadname_phase[:-2]
                print(loadname_phase.upper())
                busname = df_loadname_busname[df_loadname_busname['Load_name'] == loadname_phase.upper()]['Bus_name'].values[0]
                print(busname)
                busnumber = df_busname_busnumber[df_busname_busnumber['f1c1'] == busname]['f1c2'].values[0]
                print(busnumber)
                time = row['timestep'] * 60 + row['trackingstep'] * 15
                print(time)
                P_opendss = row['p']    
                print(P_opendss)
                Q_opendss = row['q']
                print(Q_opendss)
                P_matlab = df_matlab[df_matlab['busnumber'] == busnumber]['P_kw'].values[0] * 1000
                print(P_matlab)
                Q_matlab = df_matlab[df_matlab['busnumber'] == busnumber]['Q_kvar'].values[0] * 1000
                print(Q_matlab)
                P_delta = P_matlab - P_opendss
                print(P_delta)
                Q_delta = Q_matlab - Q_opendss
                print(Q_delta)
                df_result = df_result.append({'BusName': busname, 'LoadName': loadname, 'BusNumber': busnumber, 'Time': time, 'TimeStep': i, 'TrackingStep': k, 'Phase': phase, 'Type': row['type'], 'P_matlab': P_matlab, 'Q_matlab': Q_matlab, 'P_opendss': P_opendss, 'Q_opendss': Q_opendss, 'P_delta': P_delta, 'Q_delta': Q_delta}, ignore_index=True)
            except:
                #print("Error 420")
                #quit()
                print("Error in row", index, "loadnumber", loadname_phase, ". Skipping...")
                time.sleep(10)
                continue

        df_result.to_csv('result.csv', index=False)

        # Upload the result to the database
        success = False
        trys = 0
        while not success:
            try:
                #cursor_comparison.execute("INSERT INTO comparison VALUES " + str(tuple(df_result.values)))
                #af.uploadDataframes(cursor_comparison, df_result, "result")
                sio = StringIO()
                sio.write(df_result.to_csv(index=False, header=False))
                sio.seek(0)
                cursor_comparison.copy_from(sio, 'result', columns=df_result.columns, sep=',')
                #conn_comparison.commit()
                #df_result.to_sql('result', conn_comparison, if_exists='append')
                print("Data uploaded for time step", i, "and tracking step", k)
                success = True
            except:
                trys += 1
                if trys % 10 == 0:
                    print("Could not upload data for time step", i, "and tracking step", k, ". Retrying...")
                time.sleep(1)
 