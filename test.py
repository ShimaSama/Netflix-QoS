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
from six import StringIO
from IPython.display import Image  
from sklearn.tree import export_graphviz
import pydotplus
import os  
import sys   
import shlex
from time import time
from math import modf
from struct import pack
from subprocess import Popen, PIPE


def from_string(s):
  "Convert dotted IPv4 address to integer."
  return functools.reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))
#codigo para coger trafico en pcap

#codigo para pasarlo a csv
#process = os.popen('')
#preprocessed = process.read()
#process.close()
total = 0
false_positive = 0
false_negative = 0
true_positive = 0
true_negative = 0
good = 0
bad = 0

file = sys.argv[1]

dataset = pandas.read_csv(file)
array = dataset.values
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
                
filename = 'finalized_RFC_model.sav'
loaded_model = joblib.load(filename)
for i in range (0,len(X)):
        total += 1
        is_netflix = loaded_model.predict([X[i]])
        if(is_netflix[0] == Y[i]):
                print("good")
                good += 1
                if(is_netflix[0] == "no_netflix"):
                        true_negative += 1
                else:
                        true_positive += 1
        else:
                print("bad")  
                bad += 1  
                if(is_netflix[0] == "no_netflix"): #label es no_netflix
                        false_negative += 1
                else:#label es netflix
                        false_positive += 1

#print(is_netflix)
print("true positive = " + str(true_positive)+ "---> rate = " + str(true_positive/(true_positive+false_negative)))
print("true negative = " + str(true_negative) + "---> rate = " + str(true_negative/(true_negative+false_positive)))
print("false negative = " + str(false_negative) + "---> rate = " + str(false_negative/(false_negative+true_positive)))
print("false positive = " + str(false_positive) + "---> rate = " + str(false_positive/(false_positive+true_negative)))
print("sensitivity = " + str(true_positive/(true_positive+false_negative)))
print("specifity = " + str(true_negative/(true_negative+false_positive)))
print("acurracy = " + str(good/total))



