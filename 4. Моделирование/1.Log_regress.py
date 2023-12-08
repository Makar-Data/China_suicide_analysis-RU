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
label_encoder = preprocessing.LabelEncoder()
df = df.apply(label_encoder.fit_transform)

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