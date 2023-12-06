--���������� ��������--
SELECT Occupation, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Occupation
ORDER BY Amount DESC;

SELECT Education, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Education
ORDER BY Amount DESC;

SELECT Method, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Method
ORDER BY Amount DESC;