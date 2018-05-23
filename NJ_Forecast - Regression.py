import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from scipy.stats import linregress

# x1=np.array([130400,171095,306000,442000,596000,1568508,1876700,2109250],dtype=np.float64)
# x2=np.array([14790,134093,285387,1010684,1958993,1966580,2246134,2228775],dtype=np.float64)
# y=np.array([650,119,119,168,264,275,289,288]
x1 = np.array([1568508,1876700,2109250], dtype=np.float64)
x2 = np.array([1966580,2246134,2228775], dtype=np.float64)
# y=np.array([264,275,289,288])
y = np.array([275,289,215])
#ones = np.ones(x1.shape)
#x = np.vstack([x1, x2]).T
x = np.column_stack([x1,x2])
clf = linear_model.LinearRegression()
clf.fit(x, y)
# print(clf.predict([3128300,3114759]))
print(clf.predict([10,5]))
print(linregress(x1,y))
print(linregress(x2,y))
