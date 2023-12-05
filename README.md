# Suicide Analysis Project

Аналитический обзор [статистики суицидов](https://www.kaggle.com/datasets/utkarshx27/suicide-attempts-in-shandong-china) в Шаньдуне, Китай (2009-2011).

Цель - практика навыков чистки данных, проверки статистических гипотез, создания регрессионных моделей и визуализации данных.

По сравнению с аграрным, в индустриальном и информационном обществах фиксируется большое количество психических расстройтсв и суицидов. Анализ демографических данных Шаньдуня позволит прийти к пониманию факторов, влияющих на суицидальное поведение человека, и провести сравнение показателей между городской и сельской местностью.

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

Датасет [suicide_china_original](suicide_china_original.csv) уже находился в пригодном состоянии. Проведены несложные процедуры очистки SQL Server:
- Проверка на дубликаты колонок
- Проверка на дубликаты наблюдений
- Проверка на NaN-значения
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
(CASE WHEN Urban = 'yes' THEN 1 ELSE 0 END) AS Urban,
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

[SQL документ](1.Data_clean.sql) кода приведён в репозитории.

В итоге получаем таблицу [suicide_china](suicide_china.rpt), готовую к анализу.

---

## Этап 2. Exploratory Data Analysis
Для практики вместо сводных таблиц Pandas использовались, где это возможно, таблицы SQL Server.

https://www.kaggle.com/code/micaeld/suicide-attempts-in-shandong-eda
https://www.kaggle.com/code/alptugyilmaz/suicide-attempts-in-shandong-china-eda
https://www.kaggle.com/code/usman5659/sucide-attempts-in-china-shandongeda

Сначала была произведена оценка временных рамок и хронологического распределения наблюдений. Каждый год (2009, 2010, 2011) состоял из 12 месяцев \[0.1]. Случаи были сгруппированы по годам и кварталам и занесены в сводную таблцицу с процентным соотношением \[0.2].

С помощью Python и Pyodbc была создана гистограмма хронологического распределения случаев:
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

df['YrMth'] = pd.to_datetime(df['YrMth'])
df['YrMth'] = df['YrMth'].dt.date.apply(lambda x: x.strftime('%Y-%m'))

colors = {1: 'tab:blue', 2: 'tab:blue',
          3: 'tab:green', 4: 'tab:green', 5: 'tab:green',
          6: 'tab:red', 7: 'tab:red', 8: 'tab:red',
          9: 'tab:olive', 10: 'tab:olive', 11: 'tab:olive',
          12: 'tab:blue'}

legend = [Patch(facecolor='tab:blue', edgecolor='tab:blue', label='Winter'),
          Patch(facecolor='tab:green', edgecolor='tab:green', label='Spring'),
          Patch(facecolor='tab:red', edgecolor='tab:red', label='Summer'),
          Patch(facecolor='tab:olive', edgecolor='tab:olive', label='Autumn'),]

print(df)

plt.style.use("seaborn")

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

