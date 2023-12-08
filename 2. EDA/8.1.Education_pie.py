import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Education, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Education
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Визуализация
palette = sns.color_palette('hls', len(df))
plt.style.use('seaborn')

fig, ax = plt.subplots()
ax.pie(df['Amount'], autopct='%1.1f%%',
              labels=df['Education'] + ' ' + '(' + df['Amount'].astype(str) + ')',
              pctdistance=0.8, labeldistance=1.05, colors=palette,
              wedgeprops={'edgecolor': 'black', 'linewidth': 0.3})

fig.suptitle('Education Ratio')

plt.tight_layout()
plt.show()