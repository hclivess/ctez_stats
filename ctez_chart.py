import matplotlib.pyplot as plt
import numpy as np
import json

# Data for plotting

with open("outfile.txt", "r+") as infile:
    input_dict = json.loads(infile.read())

x_axis = input_dict.keys()
y_axis = input_dict.values()

fig, ax = plt.subplots()
ax.plot(x_axis, y_axis)

ax.set(xlabel='timestamp',
       ylabel='drift',
       title='ctez drift over time')
ax.grid()

plt.xticks(rotation=90)

fig.savefig("drift.png")
plt.show()
