import numpy as np
import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Age, Died
FROM suicide_china;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Разделение категорий на разные группы
df_died = df.loc[df['Died'] == 1]
df_lived = df.loc[df['Died'] == 0]
dfs = [df['Age'], df_died['Age'], df_lived['Age']]

# Тесты соответствия нормальному распределению
print('Shapiro-Wilk Test:')
for dataframe in dfs:
    print(stats.shapiro(dataframe))

print('\nKolmogorov-Smirnov Test:')
for dataframe in dfs:
    dist = getattr(stats, 'norm')
    param = dist.fit(dataframe)
    result = stats.kstest(dataframe, 'norm', args=param)
    print(result)

# Тест Манна-Уитни
sample1 = df_died['Age']
sample2 = df_lived['Age']

results = stats.mannwhitneyu(sample1, sample2)
u = results[0]
mean = (len(sample1) * len(sample2)) / 2
std = np.sqrt((len(sample1) * len(sample2) * (len(sample1) + len(sample2) + 1)) / 12)
z = (u - mean) / std

print('\nMann-Whitney Test:')
print(results)
print('Z-critical:', z)

# Визуализация
dfd = df_died.groupby(['Age'], as_index=False).agg('count')
dfd.rename(columns={'Died': 'Amount'}, inplace=True)
dfl = df_lived.groupby(['Age'], as_index=False).agg('count')
dfl.rename(columns={'Died': 'Amount'}, inplace=True)

plt.style.use('seaborn')

fig1 = plt.figure()

ax1 = fig1.add_subplot(121)
ax1.bar(dfd['Age'], dfd['Amount'], alpha=0.5)
ax1.set_xlabel('Age')
ax1.set_ylabel('Cases')
ax2 = fig1.add_subplot(122)
ax2.bar(dfl['Age'], dfl['Amount'], alpha=0.5)
ax2.set_xlabel('Age')
fig1.suptitle('Age Distribution')
plt.tight_layout()

fig2 = plt.figure()

ax3 = fig2.add_subplot()
ax3.bar(dfd['Age'], dfd['Amount'], alpha=0.5, color='tab:red', label='Died')
ax3.bar(dfl['Age'], dfl['Amount'], alpha=0.5, color='tab:blue', label='Survived')
ax3.set_ylabel('Cases')
fig2.suptitle('Age Distribution')
plt.legend()
plt.tight_layout()

fig3 = plt.figure()

ax4 = fig3.add_subplot()
ax4.boxplot([dfd['Age'], dfl['Age']])
plt.xticks([1, 2], ['Died', 'Survived'])
fig3.suptitle('Age Distribution')
plt.tight_layout()

plt.show()