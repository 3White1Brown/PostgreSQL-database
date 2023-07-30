import psycopg2
from psycopg2 import Error
from sqlalchemy import create_engine, text
import pandas as pd
from pathlib import Path
import pandas as pd
import numpy as np


def run_sql_from_file(sql_file):
    '''
	read a SQL file with multiple stmts and process it
	adapted from an idea by JF Santos
	Note: not really needed when using dataframes.
    '''
    sql_command = ''
    for line in sql_file:
        #if line.startswith('VALUES'):        
     # Ignore commented lines
        if not line.startswith('--') and line.strip('\n'):        
        # Append line to the command string, prefix with space
           sql_command +=  ' ' + line.strip('\n')
           #sql_command = ' ' + sql_command + line.strip('\n')
        # If the command string ends with ';', it is a full statement
        if sql_command.endswith(';'):
            # Try to execute statement and commit it
            try:
                #print("running " + sql_command+".") 
                psql_conn.execute(text(sql_command))
                #psql_conn.commit()
            # Assert in case of error
            except:
                print('Error:'+sql_command + "." + psql_conn.error())
                ret_ =  False
            # Finally, clear command string
            finally:
                sql_command = ''           
                ret_ = True
    return ret_


connection.autocommit = True

# Create a cursor to perform database operations
cursor = connection.cursor()
# Print PostgreSQL details
print("PostgreSQL server information")
print(connection.get_dsn_parameters(), "\n")
# Executing a SQL query
cursor.execute("SELECT version();")


# Fetch result
record = cursor.fetchone()
print("You are connected to - ", record, "\n")
cursor.close()

DIALECT = 'postgresql+psycopg2://'
db_uri = "%s:%s@%s/%s" % (user, password, host, database)
print(DIALECT+db_uri)

#########################################################################
# Use create_engine method and form a connection--> closest to SQL syntax
#########################################################################
engine = create_engine(DIALECT + db_uri)
psql_conn = engine.connect()
if not psql_conn:
    print("DB connection is not OK!")
else:
    print("DB connection is OK.")

print("\n", "=^.^= "*10)
print("Creating SQL tables")
query1 = text('''SELECT Vaccine.id, Diagnosis.symptom, COUNT(*) as frequency, 1.0 * COUNT(*)/(SELECT COUNT(*) from Symptoms) AS relative_frequency FROM Symptoms 
JOIN Diagnosis on Symptoms.name = Diagnosis.symptom JOIN 
(Attends NATURAL JOIN Vaccination) ON Diagnosis.ssNo = Attends.ssNo
 JOIN Batch on Vaccination.batchid = Batch.id JOIN Manufacturer ON Batch.manufacturerid = Manufacturer.id
 JOIN Vaccine ON Manufacturer.vaccineid = Vaccine.id WHERE Vaccination.date <= Diagnosis.date GROUP BY Vaccine.id, Diagnosis.Symptom''')
result1 = pd.read_sql_query(query1, psql_conn)
print(result1)
query1 = text('''SELECT COUNT(*) from Symptoms''')
result1 = pd.read_sql_query(query1, psql_conn)
print(result1)
# sql_file = open('.\\database\\tableScript.sql', 'r')
# run_sql_from_file(sql_file)
# sql_file.close()

# print("Done!")

# # Commit changes
# # psql_conn.commit()

# # ---------------------- Adding data to the db ----------------------
# filePath = ".\\data\\vaccine-distribution-data.xlsx"
# excel_file = pd.ExcelFile(filePath)

# tables = {}
# for sheet_name in excel_file.sheet_names:
#     tables[sheet_name] = pd.read_excel(filePath, sheet_name=sheet_name)

# for table in tables.values():
#     table.drop(list(filter(lambda x: x.startswith("Unnamed"), list(table.keys()))), axis = 1, inplace = True)

# excel_file.close()

# # Renaming columns
# tables['VaccineType'].rename(columns={'doses': 'dosage', 'ID': 'id', 'tempMin': 'tempmin', 'tempMax': 'tempmax'}, inplace=True)
# tables['Manufacturer'].rename(columns={'vaccine': 'vaccineid', 'ID': 'id'}, inplace=True)
# tables['VaccineBatch'].rename(columns={'expiration': 'expirydate', 'manufacturer': 'manufacturerid', "batchID": 'id', 'amount': 'numberofvaccines', 'manufDate': 'manufactureddate', 'location': 'healthcarefacilityname'}, inplace=True)
# tables['StaffMembers'].rename(columns={'social security number': 'ssno', 'date of birth': 'birthday', 'vaccination status': 'vaccinationstatus', 'hospital': 'healthcarefacilityname'}, inplace = True)
# tables['Shifts'].rename(columns={'weekday': 'workday', 'worker': 'ssno'}, inplace = True)
# tables['Transportation log'].rename(columns={'batchID': 'batchid', 'arrival': 'tolocation', 'departure ': 'fromlocation', 'dateArr': 'arrivaldate', 'dateDep': 'departuredate'}, inplace = True)
# tables['Patients'].rename(columns={'ssNo': 'ssno', 'date of birth': 'birthday'}, inplace=True)
# tables['VaccinePatients'].rename(columns = {'location': 'healthcarefacilityname', 'patientSsNo': 'ssno'}, inplace = True)
# tables['Patients'].rename(columns={'date of birth': 'birthday'}, inplace = True)
# tables['Vaccinations'].rename(columns={'location ': 'healthcarefacilityname', 'batchID': 'batchid'}, inplace = True)
# tables['Diagnosis'].rename(columns={'patient': 'ssno', }, inplace = True)

# # Dropping, adding & modifying some columns
# tables['VaccineBatch'].drop(['type'], axis=1, inplace = True)
# tables['Shifts'].drop(['station'], axis=1, inplace = True)
# tables['Patients'] = pd.merge(tables['Patients'], tables['VaccinePatients'].groupby('ssno').size().reset_index(name='vaccinationstatus'), on='ssno', how='outer')
# tables['Patients']['vaccinationstatus'].fillna(0, inplace=True)
# weekday_mapping = {
#     'Monday': 1,
#     'Tuesday': 2,
#     'Wednesday': 3,
#     'Thursday': 4,
#     'Friday': 5,
#     'Saturday': 6,
#     'Sunday': 7
# }
# tables['Shifts']['workday'] = tables['Shifts']['workday'].map(weekday_mapping)
# # Inside the date we had Feb 29th 2021 - a non-existing date; we decided to convert it to Feb 28th instead
# replacement_date = pd.Timestamp('2021-02-28')
# tables['Diagnosis']['date'] = pd.to_datetime(tables['Diagnosis']['date'], errors='coerce').fillna(replacement_date)
# tables['Diagnosis'].reset_index(drop=True, inplace=True)

# # Pushing into the database 
# tables['VaccineType'].to_sql('vaccine', psql_conn, if_exists='append', index=False)
# tables['Manufacturer'].to_sql('manufacturer', psql_conn, if_exists='append', index=False)
# tables['VaccinationStations'].to_sql('healthcarefacility', psql_conn, if_exists='append', index=False)
# tables['VaccineBatch'].to_sql('batch', psql_conn, if_exists='append', index=False)
# tables['StaffMembers'].to_sql('staff', psql_conn, if_exists='append', index=False)
# tables['Shifts'].to_sql('shift', psql_conn, if_exists='append', index=False)
# tables['Transportation log'].to_sql('transportationlog', psql_conn, if_exists='append', index=False)
# tables['Patients'].to_sql('patient', psql_conn, if_exists='append', index=False)
# tables['Vaccinations'].to_sql('vaccination', psql_conn, if_exists='append', index=False)
# tables['VaccinePatients'].to_sql('attends', psql_conn, if_exists='append', index=False)
# tables['Symptoms'].to_sql('symptoms', psql_conn, if_exists='append', index=False)
# tables['Diagnosis'].to_sql('diagnosis', psql_conn, if_exists='append', index=False)

# print(pd.read_sql_query('''select * from "Symptoms" limit 5''', psql_conn))
# Close connection
psql_conn.close()
