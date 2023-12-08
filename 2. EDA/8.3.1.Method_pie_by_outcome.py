import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Method, Died, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Method, Died
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
df_died = df.loc[df['Died'] == 1]
df_lived = df.loc[df['Died'] == 0]

# Визуализация
plt.style.use('seaborn')
palette = sns.color_palette('hls', len(df))
signified = df['Method'].unique()
signifiers = palette.as_hex()
unified_palette = {signified[i]: signifiers[i] for i in range(df['Method'].nunique())}
died_palette = [unified_palette[signified] for signified in df_died['Method'].unique()]
lived_palette = [unified_palette[signified] for signified in df_lived['Method'].unique()]

fig = plt.figure()
fig.suptitle('Methods by Outcome')

ax1 = fig.add_subplot(121)
ax1.set_title('Died')
ax1.pie(df_died['Amount'], autopct='%1.1f%%', pctdistance=0.8, colors=died_palette,
              wedgeprops={'edgecolor': 'black', 'linewidth': 0.3})
ax1.legend(labels=df_died['Method'] + ' ' + '(' + df_died['Amount'].astype(str) + ')',
           loc=(0,-0.2), ncol=2)

ax2 = fig.add_subplot(122)
ax2.set_title('Survived')
ax2.pie(df_lived['Amount'], autopct='%1.1f%%', pctdistance=0.8, colors=lived_palette,
              wedgeprops={'edgecolor': 'black', 'linewidth': 0.3})
ax2.legend(labels=df_lived['Method'] + ' ' + '(' + df_lived['Amount'].astype(str) + ')',
           loc=(0,-0.2), ncol=2)

plt.grid(visible=False)
plt.tight_layout()
plt.show()