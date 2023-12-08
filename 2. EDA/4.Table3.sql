--������� 3--
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



SELECT *, 
CONCAT(CAST(ROUND(CAST(Died AS FLOAT)/CAST(Total AS FLOAT), 2)*100 AS VARCHAR(10)), '%') AS Death_Rate

FROM (
	SELECT Age_Interval,
	COUNT(CASE WHEN Died = 1 THEN 1 ELSE NULL END)
	AS Died,
	COUNT(CASE WHEN Died = 0 THEN 1 ELSE NULL END)
	AS Survived,
	COUNT(*) AS Total
	
	FROM suicide_china
	GROUP BY Age_Interval
	) Src
ORDER BY Age_Interval;



SELECT *, 
CONCAT(CAST(ROUND(CAST(Hospitalised AS FLOAT)/CAST(Total AS FLOAT), 2)*100 AS VARCHAR(10)), '%') AS Hosp_Rate

FROM (
	SELECT Died,
	COUNT(CASE WHEN Hospitalised = 1 THEN 1 ELSE NULL END)
	AS Hospitalised,
	COUNT(CASE WHEN Hospitalised = 0 THEN 1 ELSE NULL END)
	AS Not_Hospitalised,
	COUNT(*) AS Total
	
	FROM suicide_china
	GROUP BY Died
	) Src;



SELECT *, 
CONCAT(CAST(ROUND(CAST(Urban AS FLOAT)/CAST(Total AS FLOAT), 2)*100 AS VARCHAR(10)), '%') AS Urban

FROM (
	SELECT Method,
	COUNT(CASE WHEN Urban = 1 THEN 1 ELSE NULL END)
	AS Urban,
	COUNT(CASE WHEN Urban = 0 THEN 1 ELSE NULL END)
	AS Rural,
	COUNT(*) AS Total
	
	FROM suicide_china
	GROUP BY Method
	) Src;



SELECT *, 
CONCAT(CAST(ROUND(CAST(Males AS FLOAT)/CAST(Total AS FLOAT), 2)*100 AS VARCHAR(10)), '%') AS Males_perc

FROM (
	SELECT Method,
	COUNT(CASE WHEN Sex = 'male' THEN 1 ELSE NULL END)
	AS Males,
	COUNT(CASE WHEN Sex = 'female' THEN 1 ELSE NULL END)
	AS Females,
	COUNT(*) AS Total
	
	FROM suicide_china
	GROUP BY Method
	) Src;