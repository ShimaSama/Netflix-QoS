# -*- coding: utf-8 -*-

# Load libraries
import pandas
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
import joblib
import functools
#from sklearn.externals import joblib
#from sklearn.externals.six import StringIO  
from six import StringIO
from IPython.display import Image  
from sklearn.tree import export_graphviz
import pydotplus
import os  
import sys   

def from_string(s):
  "Convert dotted IPv4 address to integer."
  return functools.reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

# load dataset
file = sys.argv[1]
#file2 = sys.argv[2]
dataset = pandas.read_csv(file)
#dataset2 = pandas.read_csv(file2)
#dataset = dataset + dataset2
print (dataset.shape)

# head
print(dataset.head(20))

# descriptions
print(dataset.describe())

# class distribution
print(dataset.groupby('label').size())

# split dataset
array = dataset.values
print(array)
X = array[:,2:32]
Y = array[:,32]
validation_size = 0.30
seed = 42
for elem in X:
        count=0
        elem[9]=from_string(elem[9])
        elem[10]=from_string(elem[10])
        for elem2 in elem:
                
                if type(elem2)==str and elem2.startswith('0x'):
                     
                        elem[count]=int(elem2, 16)
                        
                
                count += 1
                
    

X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size, random_state=seed)
X_train_set, X_test, Y_train_set, Y_test = model_selection.train_test_split(X_train, Y_train, test_size=validation_size, random_state=seed)

# Test options and evaluation metric
scoring = 'accuracy'

# valuating algorithm model
models = []
models.append(('LR', LogisticRegression(max_iter=200)))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('RFC', RandomForestClassifier()))

# evaluate each model in turn
results = []
names = []
for name, model in models:

        kfold = model_selection.KFold(n_splits=5, random_state=seed, shuffle=True)
        cv_results = model_selection.cross_val_score(model, X_train, Y_train, cv=kfold, scoring=scoring)
        results.append(cv_results)
        names.append(name)
        msg = "%s Accuracy: %f (+/- %f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)

#Compare Algorithms
fig = plt.figure()
fig.suptitle('Algorithm Comparison')
ax = fig.add_subplot(111)
plt.boxplot(results)
ax.set_xticklabels(names)
plt.show()

# Make predictions on validation dataset
print("RFC result 30% test set")
rfc = RandomForestClassifier(n_estimators=10)
rfc.fit(X_train_set, Y_train_set)
filename = 'finalized_RFC_model.sav'
joblib.dump(rfc, filename)
# load the model from disk
loaded_model = joblib.load(filename)
result = loaded_model.score(X_test, Y_test)
print (result)

predictions_rfc = rfc.predict(X_test)
print("RFC accuracy test: \n")
print(accuracy_score(Y_test, predictions_rfc))
print(confusion_matrix(Y_test, predictions_rfc))
print(classification_report(Y_test, predictions_rfc))

# Make predictions on test dataset
print("RFC result final 30% validation")
newrfc = RandomForestClassifier(n_estimators=10)
newrfc.fit(X_train_set, Y_train_set)
newpredictions_rfc = newrfc.predict(X_validation)
print("RFC accuracy validation: \n")
print(accuracy_score(Y_validation, newpredictions_rfc))
print(confusion_matrix(Y_validation, newpredictions_rfc))
print(classification_report(Y_validation, newpredictions_rfc))

# Feature Importance
print ("Validating Feature importance")
# fit an Extra Trees model to the data
test_model = RandomForestClassifier()
test_model.fit(X_train, Y_train)
# display the relative importance of each attribute
print(test_model.feature_importances_)
# plot
plt.bar(range(len(test_model.feature_importances_)), test_model.feature_importances_)
plt.show()
#
df = dataset.reset_index(drop = False)
feat_importances = pandas.Series(test_model.feature_importances_, index=dataset.columns[2:32])
feat_importances.nlargest(20).plot(kind='barh')


#rfc export
estimator = newrfc.estimators_[5]
export_graphviz(newrfc.estimators_[1], out_file='multi-tree.dot',
                 filled=True, rounded=True,
                 feature_names = dataset.columns[2:32],
                 class_names = dataset.columns[32],
                 proportion = False, precision=2,
                 special_characters=True)

