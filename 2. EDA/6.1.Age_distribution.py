import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Age, COUNT(*) AS Amount
FROM suicide_china
WHERE Education IN ('secondary', 'iliterate')
GROUP BY Age
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Визуализация
plt.style.use('seaborn')

fig, ax = plt.subplots()
bars = ax.bar(df['Age'], df['Amount'], alpha=0.8)

fig.suptitle('Age Distribution')
ax.set_ylabel('Cases')

plt.tight_layout()
plt.show()