import os.path
import matplotlib.pyplot as plt
import numpy as np
import json


# Data for plotting

def chart():
    with open("outfile.json", "r+") as infile:
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

    if not os.path.exists("static"):
        os.makedirs("static")

    fig.savefig("static/drift.png")
    #plt.show()

if __name__ == "__main__":
    chart()