#Additional functions to use in the main code
import psycopg2 as pg
import pandas as pd
from sqlalchemy import create_engine

def uploadTransversionFiles():
    #Upload the files for the transversion of OpenDSS to Matlab and vice versa
    #The files are stored in the same folder
    #Take care of the order of the files as they are hardcoded
    
    engine = create_engine('postgresql://seto_db_user:seto_db_pwd@192.168.1.90:5488/setocomparisondb')
    df = pd.read_csv('DER_Bus_Data.csv')
    df.to_sql('der_bus_data', engine, if_exists='replace')
    df = pd.read_csv('Loadinfo.csv')
    df.to_sql('loadinfo', engine, if_exists='replace')
