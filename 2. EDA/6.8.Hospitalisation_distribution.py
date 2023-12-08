import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Hospitalised, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Hospitalised
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
decoded = {1: 'hospitalised', 0: 'not hospitalised'}
df['New_Hosp'] = df['Hospitalised'].replace(decoded)

# Визуализация
plt.style.use('seaborn')

fig, ax = plt.subplots()
bars = ax.bar(df['New_Hosp'], df['Amount'], alpha=0.8)

fig.suptitle('Hospitalisation Distribution')
ax.bar_label(bars)
ax.tick_params(axis='x', labelrotation=25)
ax.set_ylabel('Cases')

plt.tight_layout()
plt.show()