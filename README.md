# Suicide Analysis Project

Аналитический обзор [статистики суицидов](https://www.kaggle.com/datasets/utkarshx27/suicide-attempts-in-shandong-china) в Шаньдуне, Китай (2009-2011).

Цель - практика навыков чистки данных, проверки статистических гипотез, создания регрессионных моделей и визуализации данных.

По сравнению с аграрным, в индустриальном и информационном обществах фиксируется большое количество психических расстройтсв и суицидов. Анализ демографических данных Шаньдуня позволит прийти к пониманию факторов, влияющих на суицидальное поведение человека, и провести сравнение показателей между городской и сельской местностью.

![Shandong](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/5cd5847d-c302-49ee-847b-ca991f723b70)
<p align="center">
Карта 2020 г. ([Meng et al, 2021](https://www.mdpi.com/2073-445X/10/6/639))
</p>

Вопросы:
- Какие демографические группы риска можно выделить?
- Что является предикторами метода, исхода попыток суицида и госпитализации?
- В чём заключается разница между наблюдениями в городах и сеьской местности?
- Какие рекоммендации возможно сделать на основе имеющихся данных?
- Какие дополнительные сведения необходимы для более глубокого исследования?
  
Выводы:
1. ...
2. ...
3. ...
4. ...
5. ...
   
---

## Этап 1. Чистка и преобразование данных

Датасет suicide_china_original [[1]](suicide_china_original.csv) уже находился в пригодном состоянии. Проведены несложные процедуры очистки SQL Server:
- Проверка на дубликаты колонок
- Проверка на дубликаты наблюдений
- Проверка на NaN-значения [(взято у hkravitz)](https://stackoverflow.com/a/37406536)
- Переименование полей с названиями, совпадающими с синтаксисом SQL
- Перевод значений в строчные буквы
- Удаление лишних значений
- Перевод бинарных значений в 1 и 0
- Перенос очищенных данных в новую таблицу для сохранения целостности оригинала
```SQL
--Проверка равенства column1 и Person_ID--
SELECT *, CASE WHEN entries = of_them_equal THEN 1 ELSE 0 END AS col_equality_check
FROM (
SELECT COUNT(*) AS entries,
COUNT(CASE WHEN column1 = Person_ID THEN 1 ELSE 0 END) AS of_them_equal
FROM suicide_china_original ) Src;

--Проверка на дубликаты наблюдений--
SELECT Person_ID, Hospitalised, Died, Urban, [Year], [Month], Sex, Age, Education, Occupation, Method, COUNT(*) as Amount
FROM suicide_china_original
GROUP BY Person_ID, Hospitalised, Died, Urban, [Year], [Month], Sex, Age, Education, Occupation, Method
HAVING COUNT(*) > 1;

--Проверка на NaN-значения--
SET NOCOUNT ON
DECLARE @Schema NVARCHAR(100) = 'dbo'
DECLARE @Table NVARCHAR(100) = 'suicide_china_original'
DECLARE @sql NVARCHAR(MAX) =''
IF OBJECT_ID ('tempdb..#Nulls') IS NOT NULL DROP TABLE #Nulls

CREATE TABLE #Nulls (TableName sysname, ColumnName sysname, ColumnPosition int, NullCount int, NonNullCount int)

SELECT @sql += 'SELECT
'''+TABLE_NAME+''' AS TableName,
'''+COLUMN_NAME+''' AS ColumnName,
'''+CONVERT(VARCHAR(5),ORDINAL_POSITION)+''' AS ColumnPosition,
SUM(CASE WHEN '+COLUMN_NAME+' IS NULL THEN 1 ELSE 0 END) CountNulls,
COUNT(' +COLUMN_NAME+') CountnonNulls
FROM '+QUOTENAME(TABLE_SCHEMA)+'.'+QUOTENAME(TABLE_NAME)+';'+ CHAR(10)

FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = @Schema
AND TABLE_NAME = @Table

INSERT INTO #Nulls 
EXEC sp_executesql @sql

SELECT * 
FROM #Nulls

DROP TABLE #Nulls;

--Форматирование и очистка--
SELECT
Person_ID,
(CASE WHEN Hospitalised = 'yes' THEN 1 ELSE 0 END) AS Hospitalised,
(CASE WHEN Died = 'yes' THEN 1 ELSE 0 END) AS Died,
(CASE WHEN Urban = 'yes' THEN 1 
WHEN Urban = 'no' THEN 0 ELSE NULL END) AS Urban,
[Year] AS Yr,
[Month] AS Mth,
Sex,
Age,
LOWER(TRIM(Education)) AS Education,
Occupation,
LOWER(TRIM(method)) AS Method

INTO suicide_china

FROM suicide_china_original;
```

Поля месяцев и возрастов были сложно читаемы из-за большого количества уникальных значений. Для упрощения восприятия значения были объеденены в квартали и возрастные интервалы соответственно:
- Создание колонки годовых кварталов на основе колонки месяцев
- Создание колонки возрастных интервалов на основе колонки возрастов
```SQL
--Кварталы--
ALTER TABLE suicide_china
ADD Quart nvarchar(10);

UPDATE suicide_china
SET Quart = Qrt
FROM suicide_china
INNER JOIN (

SELECT Person_ID,
CASE 
WHEN Mth BETWEEN 1 AND 3 THEN 'Q1'
WHEN Mth BETWEEN 4 AND 6 THEN 'Q2'
WHEN Mth BETWEEN 7 AND 9 THEN 'Q3'
WHEN Mth BETWEEN 10 AND 12 THEN 'Q4'
END AS Qrt
FROM suicide_china

) AS Src
ON suicide_china.Person_ID = Src.Person_ID;

--Возрастные интервалы--
ALTER TABLE suicide_china
ADD Age_Interval nvarchar(10);

UPDATE suicide_china
SET Age_Interval = Age_Int
FROM suicide_china
INNER JOIN (

SELECT Person_ID,
CASE
WHEN Age BETWEEN 0 AND 4 THEN '0-4'
WHEN Age BETWEEN 5 AND 9 THEN '5-9'
WHEN Age BETWEEN 10 AND 14 THEN '10-14'
WHEN Age BETWEEN 15 AND 19 THEN '15-19'
WHEN Age BETWEEN 20 AND 24 THEN '20-24'
WHEN Age BETWEEN 25 AND 29 THEN '25-29'
WHEN Age BETWEEN 30 AND 34 THEN '30-34'
WHEN Age BETWEEN 35 AND 39 THEN '35-39'
WHEN Age BETWEEN 40 AND 44 THEN '40-44'
WHEN Age BETWEEN 45 AND 49 THEN '45-49'
WHEN Age BETWEEN 50 AND 54 THEN '50-54'
WHEN Age BETWEEN 55 AND 59 THEN '55-59'
WHEN Age BETWEEN 60 AND 64 THEN '60-64'
WHEN Age BETWEEN 65 AND 69 THEN '65-69'
WHEN Age BETWEEN 70 AND 74 THEN '70-74'
WHEN Age BETWEEN 75 AND 79 THEN '75-79'
WHEN Age BETWEEN 80 AND 84 THEN '80-84'
WHEN Age BETWEEN 85 AND 89 THEN '85-89'
WHEN Age BETWEEN 90 AND 94 THEN '90-94'
WHEN Age BETWEEN 95 AND 99 THEN '95-99'
WHEN Age BETWEEN 100 AND 104 THEN '100-104'
WHEN Age BETWEEN 105 AND 109 THEN '105-109'
WHEN AGE BETWEEN 110 AND 114 THEN '110-114'
END AS Age_Int
FROM suicide_china

) AS ints
ON suicide_china.Person_ID = ints.Person_ID;
```

SQL документ [[2]](1.Data_clean.sql) приведён в репозитории.

В итоге получаем таблицу suicide_china [[3]](suicide_china.rpt), готовую к анализу.

---

## Этап 2. Exploratory Data Analysis
Для практики вместо сводных таблиц Pandas использовались, где это возможно, таблицы SQL Server. 

Ознакомление с уникальными значениями.
 
![0 4](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/78d9ae79-9350-4e32-8abb-ba088969fa83)

При работе с данными преимущественно использовались вариации трёх таблиц [[4]](https://github.com/Makar-Data/China_suicide_analysis-RU/tree/main/SQL_EDA):
1. Количество и пропорция наблюдений по полю
```SQL
SELECT Sex, COUNT(*) AS Amount, ROUND(CAST(COUNT(*) AS FLOAT)*100/SUM(CAST(COUNT(*) AS FLOAT)) OVER(), 2) AS Perc
FROM suicide_china 
GROUP BY Sex
ORDER BY Perc DESC;
```
![image](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/5d617278-80e7-4993-8d07-c319b93f6341)


2. Количество и пропорция наблюдений по двум полям
```SQL
SELECT Age_Interval,

CONCAT(
CAST(COUNT(CASE WHEN Sex = 'male' THEN 1 ELSE NULL END) AS VARCHAR(10)), 
' (', 
CAST((ROUND(CAST(COUNT(CASE WHEN Sex = 'male' THEN 1 ELSE NULL END) AS FLOAT)*100/SUM(CAST(COUNT(*) AS FLOAT)) OVER(), 2)) AS VARCHAR(10)), 
'%)') 
AS Males,

CONCAT(
CAST(COUNT(CASE WHEN Sex = 'female' THEN 1 ELSE NULL END) AS VARCHAR(10)), 
' (', 
CAST((ROUND(CAST(COUNT(CASE WHEN Sex = 'female' THEN 1 ELSE NULL END) AS FLOAT)*100/SUM(CAST(COUNT(*) AS FLOAT)) OVER(), 2)) AS VARCHAR(10)), 
'%)') 
AS Females,
COUNT(*) AS Total

FROM suicide_china
GROUP BY Age_Interval
ORDER BY Total DESC;
```
![image](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/e032fa95-efbc-455c-b301-49fde98fc8b2)


3. Пропорция исходов по переменной
```SQL
SELECT *, 
CONCAT(CAST(ROUND(CAST(Died AS FLOAT)/CAST(Total AS FLOAT), 2)*100 AS VARCHAR(10)), '%') AS Death_Rate

FROM (
	SELECT Method,
	COUNT(CASE WHEN Died = 1 THEN 1 ELSE NULL END)
	AS Died,
	COUNT(CASE WHEN Died = 0 THEN 1 ELSE NULL END)
	AS Survived,
	COUNT(*) AS Total
	
	FROM suicide_china
	GROUP BY Method
	) Src;
```
![image](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/e94c5474-f805-4f60-9cc5-0e65045b68a4)

Помимо приведённых таблиц, были рассмотрены другие комбинации данных. Наиболее ценные сведения:
- Все из переживших поытку суицида были госпитализированы. Лишь 19% из тех, чья попытка привела к смерти были госпитализированы. Исход попытки - главный предиктор госпитализации
- Имеется тренд на стабильный рост смертельности попыток с увеличением возраста
- На первый взгляд, половозрастное распределение в целом соответствует общему распределению Китая. Демографические сведения в целом не отличаются от общей демографии Китая (???) (а Шаньдуня?)
- Датасет состоит прежде всего из наблюдений в сельской местности (86.08%) с соответственно большой долей людей, занятых сельскохозяйственными работами (79.04%)
- Наиболее распространённые методы: употребление пестицида (68.77%), повешание (16.76%), другие яды (9.84%)
- Наименее распространённые методы:
- Наиболее смертельные методы: утопление (100%) (мб из-за определения + посмотри кто топится), повешание (97%), прыгание (80%)
- Наименее смертельные методы: неопределённый яд (3%), неопределённый (6%), другой яд (10%)
- Наблюдения разделились наполовину в соответствии с иходом суцида (51.15% - выжили, 48.85% - умерли)
- Видны сезонные флуктуации наблюдений. Во 2 квартале фиксируется максимум наблюдений, в 4 - минимум
- Хотя яды являются одними из наиболее выживаемых методов, смертность в сельской местности выше, чем в городах (51%, 40%)
- Наиболее распространённые методы женщин: другой яд (66% наблюдений использования относится к женщинам), утопление (68%), пестицид (54%)
- Наиболее распространённые методы мужчин: неопределённый (63% наблюдений использования относится к мужчинам), повешание (61%), порезы (52%) [[4]](https://github.com/Makar-Data/China_suicide_analysis-RU/tree/main/SQL_EDA)

Абсолютные цифры тоже называй, а то 1/1 тоже 100%


Сначала была произведена оценка временных рамок и хронологического распределения наблюдений. Каждый год (2009, 2010, 2011) состоял из 12 месяцев \[0.1]. Случаи были сгруппированы по годам и кварталам и занесены в сводную таблцицу с процентным соотношением \[0.2]. С помощью Python и Pyodbc был создан barplot хронологического распределения случаев:
```Python
import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT CONCAT(Yr, '-', Mth) AS YrMth,
Mth,
COUNT(*) AS Cases
FROM suicide_china
GROUP BY Yr, Mth
ORDER BY Yr, Mth;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Перевод дат в datetime формат для более лёгкого цветового выделения
df['YrMth'] = pd.to_datetime(df['YrMth'])
df['YrMth'] = df['YrMth'].dt.date.apply(lambda x: x.strftime('%Y-%m'))

# Определение цветов для месяцев и составление легенды
colors = {1: 'tab:blue', 2: 'tab:blue',
          3: 'tab:green', 4: 'tab:green', 5: 'tab:green',
          6: 'tab:red', 7: 'tab:red', 8: 'tab:red',
          9: 'tab:olive', 10: 'tab:olive', 11: 'tab:olive',
          12: 'tab:blue'}

legend = [Patch(facecolor='tab:blue', edgecolor='tab:blue', label='Winter'),
          Patch(facecolor='tab:green', edgecolor='tab:green', label='Spring'),
          Patch(facecolor='tab:red', edgecolor='tab:red', label='Summer'),
          Patch(facecolor='tab:olive', edgecolor='tab:olive', label='Autumn'),]

# Визуализация
plt.style.use('seaborn')

plt.bar(x=df['YrMth'], height=df['Cases'], color=[colors[i] for i in df['Mth']])
plt.xticks(fontsize=10, rotation=90)

plt.title('Suicide attempts in Shandong over time')
plt.xlabel('Date')
plt.ylabel('Cases')

plt.legend(handles=legend, loc='upper left')
plt.tight_layout()
plt.show()
```
![0 3](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/7973c6e6-1231-4e01-aea8-912edce9af13)

Видны сезонные тренды. В летние как правило фиксируется максимум случаев, а в зимние - минимум, что совпадает с мировыми наблюдениями https://en.wikipedia.org/wiki/Seasonal_effects_on_suicide_rates#:~:text=Research%20on%20seasonal%20effects%20on,months%20of%20the%20winter%20season

Для ознакомления с демографическим составом датасета была сделана половозрастная пирамида, подразделённая на категории в зависимости от исхода попытки суицида. Код во многом заимствован от [CoderzColumn](https://www.youtube.com/watch?v=yRFAslDEtgk&t=6s&ab_channel=CoderzColumn).
```Python
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
```
![0 4 4](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/e46b235d-6ec3-4a19-8ab8-269f93202b48)

```Python
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
```
![Диаграмма профессий](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/a369e93f-9bd6-4926-81e8-ff0c36793aae)

Аналогичный код был применён к распределению образования и методов:

![Диаграмма образования](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/642ea2a1-bf99-4b4e-9551-36c8d6191ce4)
![Одна диаграмма методов](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/a2efdfd9-f8eb-4c54-9eb3-17e261ac95f6)

Были рассмотрены методы по разным исходам
```Python
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
```
![Две диаграммы методов](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/667f7595-9761-4fb2-a369-b9082e7b4eb4)

Рассмотрение методов по возрастам
```Python
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
```
![0 5](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/619c7daf-796d-4aa8-a98f-7979ec0d6d6e)

Как результат EDA-исследования, (что узнали, как это поможет)
Комментарии в код!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

---

## Этап 3. Тестирование статистических гипотез

Датасет даёт возможность применения двух типов статистических тестов: (1) независимых выборок; (2) категорических значений.

Был задействован Хи-тест независимости категорий. Была составлена тепловая карта pvalue для полей со значениями-категориями. Алгоритм визуализации заимстован у [Shafqaat Ahmad](https://medium.com/analytics-vidhya/constructing-heat-map-for-chi-square-test-of-independence-6d78aa2b140f), ([github](https://github.com/shafqaatahmad/chisquare-test-heatmap/tree/main)).
```Python
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
```
![Chi_heatmap](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/b74fcc14-2085-4115-955b-27aea07c81ae)

Непрерывные данные представлены только полями возрастов и месяцев. Для выявления статистической значимости различий в распределении возрастов лиц, совершивших попытку суицида с летальным исходом, и выживших был применён Манна-Уитни-U-тест. Для исключения возможности использования Стьюдента-Т-теста были проведены Шапиро-Уилка-тест и Колмогоров-Смирнов-тест соответствия распределений нормальному распределению. Тесты выявили несоответствие распределений нормальности, исключив возможность применения параметрических тестов. Визуально были сравнены формы распределений [[ssylka]]. Их несоответствие требует интерпретации результатов Манна-Уитни-U-теста как отражающих ситуацию стохастического доминирования значений одного распределения над значениями другого.

Проведён тест, выявивший наличие статистически значимой разницы. Распределения занесены на один график в виде гистограмм разного цвета.
```Python
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
```
![Возрасты по исходам (один)](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/656371d3-cb34-4c06-866a-5d1bfce21db9)

---

## Этап 4. Моделирование

Тип данных датасета отсавил возможность построения моделей только логистической регрессии. В качестве целевого значения предсказаний использовался исход суицида как наиболее эвристически ценное.

Для использования в модели предикторы были отобраны на основе случайного леса. Фичи, преодолевшие условно установленный порог важности в 0.10 (Education = 0.27, Method = 0.24, Age_Interval = 0.24), перешли на последующие стадии процедуры. OOB случайного леса равнялся 0.80.

Датасет был разделён на три совокупности: тренировочную, валидирующую и тестовую в пропорции 70-15-15 соответственно.

На основе тренировочной группы, intercept равнялся 2.81, коэффициенты: Age_Interval = 0.10, Education = -1.01, Method = -0.46.

На валидирующей и тестовой выборках были сделаны confusion matrix. В последнем случае f1-score accuracy равнялся 0.78. Матрица была визуализирована.
```Python
import numpy as np
import pyodbc as db
import pandas as pd
from sklearn import metrics
from sklearn import linear_model
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns
import matplotlib.pylab as plt

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Sex, Age_Interval, Quart, Urban, Education, Occupation, Method, Died
FROM suicide_china;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
df = df.apply(preprocessing.LabelEncoder().fit_transform)

# X - предикторы, y - целевое значение (Died = 0/1)
all_X = df.iloc[:,:-1]
y = df.iloc[:,-1]

# Выбор наиболее значимых предикторов через OOB случайного леса
X_train_sel, X_test_sel, y_train_sel, y_test_sel = train_test_split(all_X, y, test_size=0.3, random_state=42)
rfc = RandomForestClassifier(random_state=0, criterion='gini', oob_score=True)
rfc.fit(X_train_sel, y_train_sel)

feature_names = df.columns[:-1]
assessed_X = []
for feature in zip(feature_names, rfc.feature_importances_):
    print(feature)
    assessed_X.append(feature)
print('OOB:', rfc.oob_score_)

predictors = [predictor for (predictor, score) in assessed_X if score > 0.1]
X = df[predictors]

# Построение модели
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

print("\ntrain sample:", len(X_train))
print("val sample:", len(X_val))
print("test sample:", len(X_test))

log_model = linear_model.LogisticRegression(solver='lbfgs')
log_model.fit(X=X_train, y=y_train)
print('\nIntercept:', log_model.intercept_)
print('Predictors:', predictors)
print('Coefficient:', log_model.coef_)

val_prediction = log_model.predict(X_val)
print('\nValidation group matrix:')
print(metrics.confusion_matrix(y_true=y_val, y_pred=val_prediction))
print(metrics.classification_report(y_true=y_val, y_pred=val_prediction))

test_predition = log_model.predict(X_test)
confmatrix = metrics.confusion_matrix(y_true=y_test, y_pred=test_predition)
print('\nTest group matrix:')
print(confmatrix)
print(metrics.classification_report(y_true=y_test, y_pred=test_predition))

# Визуализация матрицы
plt.style.use('seaborn')
class_names = [0, 1]

fig, ax = plt.subplots()

tick_marks = np.arange(len(class_names))
plt.xticks(tick_marks, class_names)
plt.yticks(tick_marks, class_names)
sns.heatmap(pd.DataFrame(confmatrix), annot=True, cmap='Blues', fmt='g')
ax.xaxis.set_label_position('top')
plt.title('Confusion matrix', y = 1.1)
plt.ylabel('Actual outcome')
plt.xlabel('Predicted outcome')

plt.tight_layout()
plt.show()
```
![Confusion_matrix](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/b393fdff-3700-4d68-af71-804650243045)

---

## Этап 4. Завершение и интерпретация результатов

Выделение образования как наиболее важного предиктора летальности не было выявлено на предыдущих этапах анализа, но подтверждается при визуальном обследовании.

![Образование_по_исходам](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/95353b1b-e593-401b-afa6-03f41338e584)

Для объяснения данного положения есть 3 основные гипотезы:

Гипотеза 1.

Гипотеза 2.

Гипотеза 3.
