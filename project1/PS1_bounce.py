# TEST PROGRAM FOR ASTR 4140
# MODIFIED by NK on 01/23/2017
# ORIGINAL FOUND AT:   http://python4astronomers.github.com/contest/bounce.html


# Additions:
#   - spawn 2 new balls every 10 frames
#   - gradually speed up all balls over time by 2% compounding
#   - randomize ball colors every frame
#   - animation runs for 1 million frames instead of 500

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

spawn_every = 10        # spawn new balls every N frames
spawn_count = 2         # how many to spawn each time
max_balls = 10**6

speedup_factor = 1.002  # speeds increase over time

# Run animation
for i in range(10**6):

    # spawn new balls
    if (i % spawn_every == 0) and (n < max_balls):
        k = min(spawn_count, max_balls - n)

        new_pos = (20 * np.random.random_sample(k*2) - 10).reshape(k, 2)
        new_vel = (0.6 * np.random.normal(size=k*2)).reshape(k, 2)
        new_sizes = 100 * np.random.random_sample(k) + 100
        new_colors = np.random.random_sample([k, 4])

        pos = np.vstack([pos, new_pos])
        vel = np.vstack([vel, new_vel])
        sizes = np.concatenate([sizes, new_sizes])
        colors = np.vstack([colors, new_colors])
        n += k

    vel *= speedup_factor   # speed up balls

    pos = pos + vel
    bounce = abs(pos) > 10      # Find balls that are outside walls
    vel[bounce] = -vel[bounce]  # Bounce if outside the walls
    pos = np.clip(pos, -10, 10)

    # vrandomize color every frame
    colors[:, 0:3] = np.random.random_sample((n, 3))

    # update plot
    circles.set_offsets(pos)
    circles.set_sizes(sizes)
    circles.set_facecolors(colors)

    pylab.draw()
    pylab.pause(0.001)
