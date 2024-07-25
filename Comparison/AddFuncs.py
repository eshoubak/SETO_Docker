#Additional functions to use in the main code

def uploadTransversionFiles():
    #Upload the files for the transversion of OpenDSS to Matlab and vice versa
    #The files are stored in the same folder

    host_address ="192.168.1.90"
    username = "seto_db_user"
    password = "seto_db_pwd"
    port = "5488"
    # Connect to the OpenDSS database
    db_name = "setoopendssdb"
    conn_string = ("host=" + host_address + " port=" + port + " dbname=" + db_name + " user=" + username + " password=" + password)
    print("Connecting to database\n	->%s" % (conn_string))
    conn_opendss = pg.connect(conn_string)
    cursor_opendss = conn_opendss.cursor()
