import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import os


db_uri = "%s:%s@%s/%s" % (user, password, host, database)
engine = create_engine(DIALECT + db_uri)
psql_conn = engine.connect()

filePath = os.path.join(os.getcwd(), 'data', 'vaccine-distribution-data.xlsx')
whosMinawhatsMina = pd.read_excel(filePath, sheet_name='Diagnosis')
whosMinawhatsMina.drop(list(filter(lambda x: x.startswith("Unnamed"), list(whosMinawhatsMina.keys()))), axis = 1, inplace = True)

sidebar_options = ['Analytical findings', 'Data Visualizations']
selected_page = st.sidebar.radio('Navigation', sidebar_options)
# 'Analytical findings' page
if selected_page == sidebar_options[0]:
    st.title(sidebar_options[0])
    st.write('''While cleaning the data pre-insertion, we stumbled upon some unsuspected characteristics in our data. ''')
    st.write(''' - Firstly, we discovered some fake/erronous dates, such as February 29th 2021: ''')
    st.dataframe(whosMinawhatsMina[pd.to_datetime(whosMinawhatsMina['date'], errors='coerce').isnull()].reset_index(drop=True))
    st.write('''We weren't sure on what to do with these false records, so, 
                assuming human error in writing down the date, we decided to replace these dates with
                February 28th 2021.''')
    st.write(''' - Another discovery was that quite many  of records inside the 'Diagnosis' table 
                came from patients who took no vaccine. Running the following SQL query: ''')
    st.code('''select * from diagnosis d 
where not exists(select ssno from attends a where d.ssno = a.ssno);''', language='sql')
    st.write('Outputs the following results: ')
    st.dataframe(pd.read_sql_query(text('''select * from diagnosis d 
                where not exists(select ssno from attends a where d.ssno = a.ssno);'''), 
                psql_conn))

# 'Data Visualizations' page
elif selected_page == sidebar_options[1]:
    # Set the title of the document
    st.title(sidebar_options[1])

    st.write(" - Vaccinated & non-vaccinated staff members for each medical facility:")
    whosMinawhatsMina = pd.read_sql_query(text('''select * from staff'''), psql_conn).groupby(['healthcarefacilityname', 'vaccinationstatus']).size().reset_index().pivot(index='healthcarefacilityname', columns='vaccinationstatus', values=0).reset_index()
    whosMinawhatsMina.columns = ['Healthcare Facility', 'non-vaccinated', 'vaccinated']
    ax_subplot = whosMinawhatsMina.plot(x='Healthcare Facility', y=['non-vaccinated', 'vaccinated'], kind='bar')
    rotation_angle = 45
    ax_subplot.set_xticklabels(whosMinawhatsMina['Healthcare Facility'], rotation=rotation_angle, ha='right')
    fig = ax_subplot.get_figure()
    
    st.pyplot(fig)
    
    # Name the first graph
    #<span style="font-size: 24px;"> blah blah blah </span>, unsafe_allow_html=True
    st.write(' - A chart containing the number of vaccines each manufacturer has shipped:')
    st.code('''SELECT SUM(numberofvaccines) as numberOfVaccines, manufacturerid FROM Batch
JOIN Manufacturer ON
Batch.manufacturerid = Manufacturer.id
GROUP BY Manufacturerid
ORDER BY numberofvaccines DESC;''')
    VPManu = pd.read_sql_query(text('''SELECT SUM(numberofvaccines) as numberOfVaccines, manufacturerid FROM Batch
                JOIN Manufacturer ON
                Batch.manufacturerid = Manufacturer.id
                GROUP BY Manufacturerid
                ORDER BY numberofvaccines DESC;'''),psql_conn)
    # Display the data frame found with SQL query
    # st.dataframe(VPManu)
    # Settings for plotting
    fig, ax = plt.subplots()
    ax.bar(VPManu['manufacturerid'], VPManu['numberofvaccines'])
    ax.set_xlabel('Manufacturer ID')
    ax.set_ylabel('Number of Vaccines')
    ax.set_title('Total Number of Vaccines by Manufacturer')
    ax.set_yticks(range(0, max(VPManu['numberofvaccines']), 20))  # Set tick values every 10 units
    ax.set_yticklabels(range(0, max(VPManu['numberofvaccines']), 20))  # Set tick labels
    # Display the plot using Streamlit
    st.pyplot(fig)
    

    # Name the second graph 
    st.write(' - A graph that tells how many people have been vaccinated at a certain hospital or clinic:')
    st.code('''SELECT V.healthcarefacilityname as hospital, COUNT(A.ssno) AS patients 
FROM Vaccination AS V
INNER JOIN Attends AS A ON V.date = A.date AND V.healthcareFacilityName = A.healthcarefacilityname
GROUP BY V.healthcarefacilityname;''')
    vacPerHospital = pd.read_sql_query(text('''SELECT V.healthcarefacilityname as hospital, COUNT(A.ssno) AS patients
                  FROM Vaccination AS V
                  INNER JOIN Attends AS A ON V.date = A.date AND V.healthcareFacilityName = A.healthcarefacilityname
                  GROUP BY V.healthcarefacilityname;'''),psql_conn)
    fig, ax = plt.subplots()
    ax.pie(vacPerHospital['patients'], labels=vacPerHospital['hospital'], autopct=lambda p: f'{int(p * sum(vacPerHospital["patients"])/100)}')

    # Add a title
    plt.title('Patients vaccinated by Healthcare Facility')

    # Display the chart
    st.pyplot(fig)

    
    st.write(' - A chart showing the appearance of symptoms in the population:')

    # Execute the SQL query and load the data into a DataFrame
    query = text('''
        SELECT EXTRACT(MONTH FROM date) AS month, criticality, COUNT(*) as no_of_symptoms 
        FROM (Diagnosis JOIN Symptoms on name = symptom) GROUP BY month, criticality;
    ''')
    df = pd.read_sql_query(query, psql_conn)

    # Map month numbers to month names with the correct order
    month_names = ['January', 'February', 'March',
                   'April', 'May', 'June']  # Corrected month order
    df['month'] = df['month'].map(lambda month: month_names[int(month) - 1])

    # Map criticality values to corresponding text labels
    df['criticality'] = df['criticality'].map(
        {1: 'Critical', 0: 'Non-Critical'})

    # Order the DataFrame by month
    df['month'] = pd.Categorical(
        df['month'], categories=month_names, ordered=True)
    df.sort_values('month', inplace=True)

    # Create the bar plot
    fig, ax = plt.subplots()

    crit_values = df['criticality'].unique()
    colors = ['red', 'blue']  # Colors for critical and non-critical bars

    for i, crit in enumerate(crit_values):
        data = df[df['criticality'] == crit]
        x = data['month']
        y = data['no_of_symptoms']
        bottom = [0] * len(x)  # Initialize bottom positions as zeros
        ax.bar(x, y, bottom=bottom, color=colors[i], label=crit)

    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Symptoms')
    ax.set_title('Symptoms Count by Month and Criticality')
    ax.legend()

    # Display the plot using Streamlit
    st.pyplot(fig)