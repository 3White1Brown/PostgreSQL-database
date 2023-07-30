import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt


db_uri = "%s:%s@%s/%s" % (user, password, host, database)
engine = create_engine(DIALECT + db_uri)
psql_conn = engine.connect()

# ------------------------------------------- TASK 1 -------------------------------------------
task1 = pd.read_sql_query('''
SELECT p.ssno as "ssNO", gender, birthday as "dateOfBirth", symptom, date as "diagnosisDate"
from patient p
join diagnosis d on d.ssno = p.ssno;''', psql_conn)
task1.to_sql('patientsymtpoms', psql_conn, index=True, if_exists='replace')
print("Patients have the following symptoms:\n", task1, '\n')

# ------------------------------------------- TASK 2 -------------------------------------------
intermediate = pd.read_sql_query('''select p.ssno, a.date, vc.name
from patient p
left join attends a on p.ssno = a.ssno
left join vaccination v on v.date = a.date and v.healthcarefacilityname = a.healthcarefacilityname
left join batch b on b.id = v.batchid
left join manufacturer m on m.id = b.manufacturerid
left join vaccine vc on vc.id = m.vaccineid;
''', psql_conn)
vaccine_rows = list()
for ssno, group in intermediate.sort_values(['date']).reset_index(drop=True).groupby(['ssno']):
    vacc0 = list(group.iloc[0]) if len(group) > 0 else [ssno, None, None]
    vacc1 = list(group.iloc[1]) if len(group) > 1 else [ssno, None, None]
    vaccine_rows.append(
        [
            ssno, 
            group.iloc[0]['date'] if len(group) > 0 else None, 
            group.iloc[0]['name'] if len(group) > 0 else None, 
            group.iloc[1]['date'] if len(group) > 1 else None, 
            group.iloc[1]['name'] if len(group) > 1 else None
        ]
    )
task2 = pd.DataFrame(vaccine_rows, columns=['patientssNO', 'date1', 'vaccinetype1', 'date2', 'vaccinetype2'])
print("Pacient's vaccination table:\n", task2, '\n')

# ------------------------------------------- TASK 3 -------------------------------------------
task3 = pd.read_sql_query('''select * from patientsymtpoms;''', psql_conn)
male = task3[task3['gender'] == 'M'].drop(['gender'], axis=1).reset_index(drop=True)
female = task3[task3['gender'] == 'F'].drop(['gender'], axis=1).reset_index(drop=True)
print("The most common female symptoms are:", ', '.join(female.groupby('symptom').size().sort_values(ascending=False)[:3].index) + '.')
print("The most common male symptoms are:", ', '.join(male.groupby('symptom').size().sort_values(ascending=False)[:3].index) + '. \n')

# ----------------------------------------- TASK 4 & 5 ------------------------------------------
task4 = pd.read_sql_query('''
SELECT ssno, name, birthday, gender, 
    CASE
        WHEN date_part('year', age(birthday)) <= 10 THEN '0-10'
        WHEN date_part('year', age(birthday)) <= 20 THEN '10-20'
        WHEN date_part('year', age(birthday)) <= 40 THEN '20-40'
        WHEN date_part('year', age(birthday)) <= 60 THEN '40-60'
        ELSE '60+'
    END AS "ageGroup",
    vaccinationstatus as "vaccinationStatus"
from patient p;''', psql_conn)
print('''Our table already has a column called 'vaccinationStatus' doing exactly 
    the same thing as the specifications of task 5, \nso here is the combined table for task 4 & 5:''', task4, '\n')

# ------------------------------------------- TASK 6 -------------------------------------------
relativeFrequencyInGroups = task4.groupby(['vaccinationStatus', 'ageGroup']).size() / task4.groupby('ageGroup').size()
task6 = pd.pivot(
    relativeFrequencyInGroups.reset_index().rename(columns={0: 'frequency'}), 
    index='vaccinationStatus', 
    columns='ageGroup', 
    values='frequency'
)
print(task6, '\n')

# ------------------------------------------- TASK 7 -------------------------------------------
pd.set_option('display.max_rows', None)
vaccine_symptoms = pd.read_sql_query('''
    SELECT DISTINCT ON (d.ssno, d.symptom, d.date) m.vaccineid AS vaccine, symptom
    FROM Batch b
    JOIN Manufacturer m ON b.manufacturerid = m.id
    JOIN Vaccination v ON v.batchid = b.id
    JOIN Attends a ON a.date = v.date AND a.healthcarefacilityname = v.healthcarefacilityname
    JOIN Diagnosis d ON d.ssno = a.ssno
    WHERE d.date >= a.date
''', psql_conn)

vaccines_administered = pd.read_sql_query('''
    SELECT m.vaccineid AS vaccine, COUNT(*)
    FROM Batch b
    JOIN Manufacturer m ON b.manufacturerid = m.id
    JOIN Vaccination v ON v.batchid = b.id
    JOIN Attends a ON a.date = v.date AND a.healthcarefacilityname = v.healthcarefacilityname
    GROUP BY vaccine
''', psql_conn)

symptom_counts_by_vaccine = pd.crosstab(vaccine_symptoms['symptom'], vaccine_symptoms['vaccine'])
symptom_frequencies_by_vaccine = symptom_counts_by_vaccine.copy()
for column in symptom_frequencies_by_vaccine.columns[0:]:
    total_doses = vaccines_administered[vaccines_administered['vaccine'] == column]['count']
    symptom_frequencies_by_vaccine[column] = symptom_frequencies_by_vaccine[column].apply(lambda x: round((x * 1.0 / total_doses), 2))

def verbalize(value):
    if value >= 0.1: return 'very common'
    elif value >= 0.05: return 'common'
    elif value > 0.0: return 'rare'
    else: return '-'

verbal_descriptions = symptom_frequencies_by_vaccine.copy()
verbal_descriptions.iloc[:, 0:] = verbal_descriptions.iloc[:, 0:].applymap(verbalize) 

print("Verbal descriptions of the relative frequencies of symptoms associated with each vaccine: \n\n", verbal_descriptions, '\n')

# ------------------------------------------- TASK 8 -------------------------------------------
patient_count = pd.read_sql_query('''
SELECT COUNT(*) from Patient;
''', psql_conn).at[0, 'count'].item()

patient_percentage_by_vaccinaiton = pd.read_sql_query('''
SELECT date, healthcarefacilityname, COUNT(DISTINCT ssNo) * 100.0/''' + str(patient_count) +  '''
as percentage_patient_attending FROM Attends
GROUP BY date, healthcarefacilityname;
''', psql_conn)

std_dev_attending_patients = patient_percentage_by_vaccinaiton['percentage_patient_attending'].std()

vaccine_percentange_by_vaccination = patient_percentage_by_vaccinaiton.copy()
vaccine_percentange_by_vaccination['percentage_patient_attending'] += std_dev_attending_patients
vaccine_percentange_by_vaccination.rename(columns={'percentage_patient_attending': 'vaccine_percentage'}, inplace=True)

print("Percentage of vaccines that should be reserved for each vaccination event: \n", vaccine_percentange_by_vaccination)

# ------------------------------------------- TASK 9 -------------------------------------------
query = text('''SELECT V.date, COUNT(A.ssno) AS total_vaccinated
                  FROM Vaccination AS V
                  INNER JOIN Attends AS A ON V.date = A.date AND V.healthcareFacilityName = A.healthcarefacilityname
                  GROUP BY V.date
                  ORDER BY V.date;''')
vaccinations = pd.read_sql_query(query, psql_conn)
vaccinations['date'] = pd.to_datetime(vaccinations['date'])

# Calculate the cumulative sum of vaccinated patients
sum = vaccinations['total_vaccinated'].cumsum()

# Plot the cumulative sum of vaccinated patients
plt.plot(vaccinations['date'].dt.strftime('%Y-%m-%d'), sum)
plt.xlabel('Date')
plt.ylabel('Total')
plt.title('Cumulative Sum Of Patients')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# Note there are 8 vaccinations, however, the dates overlap on some of them,
# which means there are only 5 distinct dates for vaccinations
# where the number of patients increases.
# From the graph we can see that the total number of patients who got vaccinated
# is around a hundred, which is in accordance to the data.


# ------------------------------------------- TASK 10 ------------------------------------------
staffMet = pd.read_sql_query('''
SELECT s.ssno, s.name
from staff s
join shift sh on sh.ssno = s.ssno
join healthcarefacility hf on hf.name = s.healthcarefacilityname
join vaccination v on v.healthcarefacilityname = hf.name
where (v.date, v.healthcarefacilityname, sh.workday) in (
    SELECT v.date, v.healthcarefacilityname, sh.workday
    from vaccination v
    join healthcarefacility hf on hf.name = v.healthcarefacilityname
    join staff s on s.healthcarefacilityname = hf.name
    join shift sh on sh.ssno = s.ssno
    where date < '2021-05-15' and date > '2021-05-05' and s.ssno = '19740919-7140' and mod(sh.workday - cast(extract(dow from date) as integer), 7) = 0
);''', psql_conn)
persMet = pd.read_sql_query('''
select p.ssno, p.name
from patient p
join attends a on a.ssno = p.ssno
where (a.date, a.healthcarefacilityname) in (
    SELECT v.date, v.healthcarefacilityname
    from vaccination v
    join healthcarefacility hf on hf.name = v.healthcarefacilityname
    join staff s on s.healthcarefacilityname = hf.name
    where date < '2021-05-15' and date > '2021-05-05' and s.ssno = '19740919-7140'
);''', psql_conn)

# Appending the roles of the persons before stacking the dataframes
staffMet['role'] = 'S'
persMet['role'] = 'P'

task10 = pd.concat([staffMet, persMet], axis = 0)
print("People with whom the ill doctor has been in contact in the past 10 days:\n", task10)

psql_conn.close()