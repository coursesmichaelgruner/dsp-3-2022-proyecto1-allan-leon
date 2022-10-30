#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

x=np.arange(0,210)
y=np.zeros(len(x))
y[0:len(x)//2]=x[0:len(x)//2]/(len(x)//2)

m=-1/(x[-1]-x[len(x)//2])
b=-m*x[-1]
y[len(x)//2:]=x[len(x)//2:]*m+b

plt.plot(x,y)
plt.show()