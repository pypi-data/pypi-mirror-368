from scipy.stats import percentileofscore
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from matplotlib.widgets import CheckButtons

data = [1, 2, 5, 5, 7]
score = np.linspace(0,10,401)
print(len(score))
print(1 in score)
# Percentile rank of value 4
kinds = ['rank', 'weak', 'mean', 'strict']
kinds = ["rank"]

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)

plots = {}

for kind in kinds:
    p = percentileofscore(data, score, kind=kind)
    plots[kind] = plt.scatter(score, p, label="HELLO " + kind)

rax = plt.axes((0.01, 0.4, 0.15, 0.15))
visibility = [True] * len(kinds)
check = CheckButtons(rax, kinds, visibility)

def func(label):
    plots[label].set_visible(not plots[label].get_visible())
    plt.draw()

check.on_clicked(func)

ax.set_xlabel('Score')
ax.set_ylabel('Percentile Rank')
ax.legend(handles=[plots[k] for k in kinds])
plt.show()