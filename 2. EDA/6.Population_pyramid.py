import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''  
SELECT Sex, Age, Died  
FROM suicide_china;  
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Повторное создание интервалов для верной последовательности и сохранения возрастов без наблюдений
df['Age_Interval'] = pd.cut(df['Age'],
                            bins=[0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49,
                                  54, 59, 64, 69, 74, 79, 84, 89, 94, 99, 104],
                            labels=['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39',
                                    '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79',
                                    '80-84', '85-89', '90-94', '95-99', '100-104'])

# Создание матрицы значений
crosstab = pd.crosstab(index=df['Age_Interval'], columns=[df['Sex'], df['Died']], dropna=False, normalize='all')
male_died = [number * 100 for number in crosstab['male'][1]]
female_died = [number * 100 for number in crosstab['female'][1]]
male_lived = [number * 100 for number in crosstab['male'][0]]
female_lived = [number * 100 for number in crosstab['female'][0]]

# Трансформация матрицы в формат, пригодный для построения пирамиды
age = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64',
       '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100-104']

pyramid_df = pd.DataFrame({'Age': age, 'Male_l': male_lived, 'Male_d': male_died,
                           'Female_d': female_died, 'Female_l': female_lived})

# Создание полей со сведениями об относительном положении сегментов гистограммы
pyramid_df['Female_Width'] = pyramid_df['Female_d'] + pyramid_df['Female_l']
pyramid_df['Male_Width'] = pyramid_df['Male_d'] + pyramid_df['Male_l']
pyramid_df['Male_d_Left'] = -pyramid_df['Male_d']
pyramid_df['Male_l_Left'] = -pyramid_df['Male_Width']

# Формирование визуализации
plt.style.use('seaborn-v0_8')
fig = plt.figure(figsize=(15,10))

plt.barh(y=pyramid_df['Age'], width=pyramid_df['Female_d'],
         color='tab:red', label='Females Died', edgecolor='black')
plt.barh(y=pyramid_df['Age'], width=pyramid_df['Female_l'], left=pyramid_df['Female_d'],
         color='tab:orange', label='Females Survived', edgecolor='black')
plt.barh(y=pyramid_df['Age'], width=pyramid_df['Male_d'], left=pyramid_df['Male_d_Left'],
         color='tab:blue', label='Males Died', edgecolor='black')
plt.barh(y=pyramid_df['Age'], width=pyramid_df['Male_l'], left=pyramid_df['Male_l_Left'],
         color='tab:cyan', label='Males Survived', edgecolor='black')

# Определение позиции и формата надписей на графике
pyramid_df['Male_d_Text'] = pyramid_df['Male_d_Left'] / 2
pyramid_df['Male_l_Text'] = (pyramid_df['Male_l_Left'] + pyramid_df['Male_d_Left']) / 2
pyramid_df['Female_d_Text'] = (pyramid_df['Female_Width'] + pyramid_df['Female_d']) / 2
pyramid_df['Female_l_Text'] = pyramid_df['Female_d'] / 2

for idx in range(len(pyramid_df)):
    alpha_ = 1 if pyramid_df['Male_d_Text'][idx] != 0.5 else 0
    alpha_ = 1 if pyramid_df['Male_l_Text'][idx] != 0 else 0
    alpha = 1 if pyramid_df['Female_d_Text'][idx] != 0 else 0
    alpha = 1 if pyramid_df['Female_l_Text'][idx] != 0 else 0
    plt.text(x=pyramid_df['Male_d_Text'][idx], y=idx,
             s='{}%'.format(round(pyramid_df['Male_d'][idx], 1)),
             fontsize=14, ha='center', va='center', alpha=alpha)
    plt.text(x=pyramid_df['Male_l_Text'][idx], y=idx,
             s='{}%'.format(round(pyramid_df['Male_l'][idx], 1)),
             fontsize=14, ha='center', va='center', alpha=alpha)
    plt.text(x=pyramid_df['Female_d_Text'][idx], y=idx,
             s='{}%'.format(round(pyramid_df['Female_l'][idx], 1)),
             fontsize=14, ha='center', va='center', alpha=alpha)
    plt.text(x=pyramid_df['Female_l_Text'][idx], y=idx,
             s='{}%'.format(round(pyramid_df['Female_d'][idx], 1)),
             fontsize=14, ha='center', va='center', alpha=alpha)

# Завершение визуализации
plt.xlim(-6, 6)
plt.xticks(range(-6, 7), ['{}%'.format(i) for i in range(-6, 7)], fontsize=14)
plt.yticks(fontsize=14)

plt.title('Suicide attempts in Shandong (2009-2011)', pad=20, fontsize=25, fontweight='bold')
plt.xlabel('Percentage of suicide attempts', fontsize=20, )
plt.ylabel('Age', fontsize=20)

plt.legend(fontsize=20, shadow=True)
plt.tight_layout()
plt.show()