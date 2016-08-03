
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import sys


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
gp = np.loadtxt(sys.argv[1])
samples = np.loadtxt(sys.argv[2])
x = []
y = []
z = []

k = 0
for row in gp:
    if row[3] > 0.15 and k % 5 == 0:
        x += [row[0]]
        y += [row[1]]
        z += [row[2]]
    k += 1

#ax.plot_surface(x, y, z, rstride=4, cstride=4, color='b')

cm = plt.cm.get_cmap('RdYlBu')
p = ax.scatter(x, y, z, c=z, marker='.', cmap=cm, vmin=0, vmax=0.2, s=35)

print samples[:,1]

p = ax.scatter(samples[:,1], samples[:,2], samples[:,3], c=samples[:,3], marker='s', cmap=cm, vmin=0, vmax=0.2, s=35)

fig.colorbar(p)

plt.show()
