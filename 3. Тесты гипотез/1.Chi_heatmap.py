import pyodbc as db
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pylab as plt

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT *
FROM suicide_china;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
df.index = df['Person_ID']
del df['Person_ID']
del df['Age']
del df['Mth']

col_names = df.columns

chi_matrix=pd.DataFrame(df,columns=col_names,index=col_names)

outercnt=0
innercnt=0
for icol in col_names:
    for jcol in col_names:
        mycrosstab=pd.crosstab(df[icol],df[jcol])
        stat, p, dof, expected=stats.chi2_contingency(mycrosstab)
        chi_matrix.iloc[outercnt,innercnt]=round(p,3)
        cntexpected=expected[expected<5].size
        perexpected=((expected.size-cntexpected)/expected.size)*100
        if perexpected < 20:
            chi_matrix.iloc[outercnt, innercnt] = 2
        if icol == jcol:
            chi_matrix.iloc[outercnt, innercnt] = 0.00
        innercnt = innercnt + 1
    outercnt = outercnt + 1
    innercnt = 0

plt.style.use('seaborn')
fig = sns.heatmap(chi_matrix.astype(np.float64), annot=True, linewidths=0.1, cmap='coolwarm_r',
            annot_kws={"fontsize": 8}, cbar_kws={'label': 'pvalue'})

fig.set_title('Chi2 Independence Test Pvalues')
plt.tight_layout()
plt.show()