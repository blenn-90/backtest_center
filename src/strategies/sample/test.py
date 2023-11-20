import numpy as np 
from pandas import DataFrame
import matplotlib.pyplot as plt

index = range(20, 28, 2)
columns = range(60, 64, 1)
df = DataFrame(np.array([[2, 13, 44, 5], [2, 53, 4, 58],[2, 33, 54, 5],[2, 34, 4, 55]]), index=index, columns=columns)
print(df)
plt.pcolor(df)
plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns)
plt.show()