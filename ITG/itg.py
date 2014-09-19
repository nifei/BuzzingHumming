import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from pylab import *

metric_file = sys.argv[1]

def calib_range(min, max, value):
    if max == None:
        max = value
    if min == None:
        min = value
    if max < value:
        max = value
    if min > value:
        min = value
    return min, max

def extend_range(min, max):
    range = max - min
    print range
    delta = abs(range) * 0.1 if abs(range) > 0 else 0.001
    max_r = max + delta
    min_r = min - delta
    return min_r, max_r

def ParseDelay(metric_file):
#- "Time", "Bitrate", "Delay", "Jitter", "Packet loss"
    with open(metric_file, 'r') as f:
        for line in f:
            if line.startswith('Time'):
                continue        
            row = [float(value) for value in line.split(' ')]
            time = row[0]
            delay = row[2]
            loss = row[4]
            yield {'time':time, 'delay':delay, 'loss':1-loss}
        f.close()

time_list = []
delay_list = []
loss_list = []
min_delay, max_delay = None, None
for item in ParseDelay(metric_file):
    delay = item['delay']
    loss = item['loss']
    min_delay, max_delay = calib_range(min_delay, max_delay, delay) 
    time_list.append(item['time'])
    delay_list.append(delay)
    loss_list.append(loss)

min_delay, max_delay = extend_range(min_delay, max_delay)

clf()
host = host_subplot(111, axes_class=AA.Axes)
plt.subplots_adjust(right=0.75)
host.set_xlabel("time")
host.set_ylabel("Delay")
host.set_ylim(min_delay, max_delay)
# FIND
p1, = host.plot(time_list, delay_list, label="Delay")

host.axis["left"].label.set_color(p1.get_color())

offset = 0

def DrawLine(xVector, yVector, ylabel="ylabel", yMin=0, yMax=2000):
    global offset
    local_offset = offset
    par = host.twinx()
    new_fixed_axis = par.get_grid_helper().new_fixed_axis
    par.axis["right"] = new_fixed_axis(loc="right", axes=par, offset=(local_offset, 0))
    par.axis["right"].toggle(all=True)
    par.set_ylabel(ylabel)
    plot, = par.plot(xVector, yVector, label=ylabel)
    par.set_ylim(yMin, yMax)
    par.axis["right"].label.set_color(plot.get_color())
    offset += 60
DrawLine(time_list, loss_list, "Loss", -0.1, 1.1)

host.legend()
if len(sys.argv) > 2:
    png_name = sys.argv[2]
    savefig(png_name)
else:
    show()
