import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Urban, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Urban
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
df['New_Urban'] = np.where(df['Urban'].isnull(), 3, df["Urban"])

decoded = {1: 'urban', 0: 'rural', 3: 'unknown'}
df['New_Urban'] = df['New_Urban'].replace(decoded)

# Визуализация
plt.style.use('seaborn')

fig, ax = plt.subplots()
bars = ax.bar(df['New_Urban'], df['Amount'], alpha=0.8)

fig.suptitle('Area Distribution')
ax.bar_label(bars)
ax.set_ylabel('Cases')

plt.tight_layout()
plt.show()