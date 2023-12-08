import pyodbc as db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''  
SELECT Person_ID, Method, Age_Interval 
FROM suicide_china
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
needed = df.pivot(index='Person_ID', columns='Age_Interval', values='Method')
new_cols = [col for col in needed.columns if col != '100-104'] + ['100-104']
needed = needed[new_cols]

category_names = ['pesticide', 'hanging', 'other poison', 'poison unspec', 'unspecified', 'cutting', 'drowning', 'jumping', 'others']
questions = list(needed.columns.values)
raws = []

list_obj_cols = needed.columns[needed.dtypes == 'object'].tolist()
for obj_col in list_obj_cols:
    needed[obj_col] = needed[obj_col].astype(pd.api.types.CategoricalDtype(categories=category_names))

list_cat_cols = needed.columns[needed.dtypes == 'category'].tolist()
for cat_col in list_cat_cols:
    dc = needed[cat_col].value_counts().sort_index().reset_index().to_dict(orient='list')
    raws.append(dc['count'])

results = [[num / sum(brackets) * 100 for num in brackets] for brackets in raws]
number_results = {questions[i]: raws[i] for i in range(len(questions))}
percentage_results = {questions[i]: results[i] for i in range(len(questions))}

palette = sns.color_palette('hls', df['Method'].nunique())

def survey(number_results, percentage_results, category_names):
    labels = list(percentage_results.keys())
    data = np.array(list(percentage_results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = palette

    fig, ax = plt.subplots(figsize=(9.2, 5))
    fig.suptitle('Methods by Age')
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5,
                label=colname, color=color)
        xcenters = starts + widths / 2
        numbers = np.array(list(number_results.values()))[:, i]

        r, g, b = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        text_label = zip(xcenters, numbers)
        for y, (x, c) in enumerate(text_label):
            alpha = 1 if c != 0 else 0
            ax.text(x, y+0.06, str(int(c)),
                    ha='center', va='center', color=text_color, alpha=alpha, fontsize=8)
    ax.legend(ncol=5, bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    return fig, ax


survey(number_results, percentage_results, category_names)

plt.tight_layout()
plt.show()