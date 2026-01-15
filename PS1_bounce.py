# TEST PROGRAM FOR ASTR 4140
# MODIFIED by NK on 01/23/2017
# ORIGINAL FOUND AT:   http://python4astronomers.github.com/contest/bounce.html


# Import and define some libraries
import pylab
import numpy as np
import matplotlib.pyplot as plt

# Set up the plot
pylab.figure(1)
pylab.clf()
pylab.axis([-10, 10, -10, 10])


# Define properties of the "bouncing balls"
n = 10
pos = (20 * np.random.random_sample(n*2) - 10).reshape(n, 2)
vel = (0.3 * np.random.normal(size=n*2)).reshape(n, 2)
sizes = 100 * np.random.random_sample(n) + 100

# Colors where each row is (Red, Green, Blue, Alpha).  Each can go
# from 0 to 1.  Alpha is the transparency.
colors = np.random.random_sample([n, 4])

# Draw all the circles and return an object ``circles`` that allows
# manipulation of the plotted circles.
circles = pylab.scatter(pos[:,0], pos[:,1], marker='o', s=sizes, c=colors)

# Run animation
for i in range(500):
    pos = pos + vel
    bounce = abs(pos) > 10      # Find balls that are outside walls
    vel[bounce] = -vel[bounce]  # Bounce if outside the walls
    circles.set_offsets(pos)    # Change the positions
    pylab.draw()
    pylab.pause(0.001)
