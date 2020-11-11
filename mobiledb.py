import csv
from datetime import datetime
import random 
import sqlite3
import pandas as pd
from pandas import DataFrame
import shutil as sh



def create_replicas(number_of_iterations):
    for i in range(number_of_iterations):
        print(i+1)
        dir = "MobileDatabases/" + str(i) + ".db"
        sh.copy2('MobileDatabases/touchmedont.db' , dir)
    
def create_mobiledb(user_id, dir):
    with open('dummy.csv') as csv_file:
        with open('single_user_mobiledb.csv', mode='w') as d_file:
            doc_w = csv.writer(d_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator = '\n')
            csv_reader = csv.reader(csv_file, delimiter=',')
    
            line_count = 0
            id = 1
            for row in csv_reader:
                if line_count != 0:
                    if(int(row[0]) == user_id):
    
                        beacon = row[3]
                        time_dt = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
    
                        # new_dt = time_dt.replace(day = 31, month = 8)
                        # time_dt = new_dt
                        # duration = random.uniform(15, 20)*60
    
                        time_e = time_dt.timestamp()
                        #duration = float(row[2])*60
                        duration = float(row[2])
                        doc_w.writerow([id, beacon, time_e, duration])
                        id = id + 1
                        
                
                line_count += 1
            print("# of lines: " + str(line_count))
    
    con = sqlite3.connect(dir)
    cur = con.cursor()
    
    a_file = open("single_user_mobiledb.csv")
    rows = csv.reader(a_file)
    
    
    
    cur.executemany("INSERT INTO log_table VALUES (?,?,?,?)", rows)
    
    cur.execute("SELECT * FROM log_table")
    print(cur.fetchall())
                
    con.commit()
    con.close()
    
def setup_mobile_dummy():
    create_replicas(10)
    for i in range(10):
        dir = "MobileDatabases/" + str(i) + ".db"
        print(dir)
        create_mobiledb(i, dir)
        
        
        
setup_mobile_dummy()
        

