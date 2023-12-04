# Suicide Analysis Project

Аналитический обзор [статистики суицидов](https://www.kaggle.com/datasets/utkarshx27/suicide-attempts-in-shandong-china) в Шаньдуне, Китай (2009-2011).

Цель - практика навыков чистки данных, проверки статистических гипотез, создания регрессионных моделей и визуализации данных.

По сравнению с аграрным, в индустриальном и информационном обществах фиксируется резкий рост количества психических расстройтсв и суицидальности. Анализ демографических данных Шаньдуня позволит не только прийти к пониманию факторов, влияющих на суицидальное поведение человека, но и провести сравнение показателей между городской и сельской местностью.

Вопросы:
- Какие демографические группы риска можно выделить?
- Что является предикторами метода, исхода попыток суицида и госпитализации?
- В чём заключается разница между наблюдениями в городской и сеьской местности?
- Какие рекоммендации возможно сделать на основе имеющихся данных?
- Какие дополнительные сведения необходимы для дальнейшего исследования проблемы?

---

### Этап 1. Чистка данных

Датасет уже находился в пригодном состоянии. Проведены несложные процедуры очистки SQL Server:
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

В итоге получаем таблицу suicide_china, готовую к анализу

---

### Этап 2. Exploratory Data Analysis
