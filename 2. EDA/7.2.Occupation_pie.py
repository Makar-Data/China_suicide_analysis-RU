import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Occupation, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Occupation
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Визуализация
palette = sns.color_palette('hls', len(df))
plt.style.use('seaborn')

fig, ax = plt.subplots()
ax.pie(df['Amount'], autopct='%1.1f%%', pctdistance=0.8, colors=palette,
              wedgeprops={'edgecolor': 'black', 'linewidth': 0.3})

fig.suptitle('Occupation Ratio')

ax.legend(labels=df['Occupation'] + ' ' + '(' + df['Amount'].astype(str) + ')',
          loc=(0.9, 0))

plt.tight_layout()
plt.show()