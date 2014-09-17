import parse
import range
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from pylab import *
import time
import re
png_name = 'delay1.png'
func_ = parse.MergePcap1
min_delay, max_delay = None, None
time_list = list()
delay_list = list()

time_before = time.time()
for item in func_('output.pcapng', 'input.pcapng', '192.168.91.253', '192.168.91.64'):
    time_list.append(item['out'])
    delay_list.append(item['delay'])
    min_delay, max_delay = range.calib_range(min_delay, max_delay, item['delay'])

time_after = time.time()
dur = time_after - time_before

min_delay, max_delay = range.extend_range(min_delay, max_delay)
print min_delay, max_delay
print time_list[-1] - time_list[0]
print len(time_list)
print dur

clf()
host = host_subplot(111, axes_class=AA.Axes)
plt.subplots_adjust(right=0.75)
host.set_xlabel("time")
host.set_ylabel("Delay")
host.set_ylim(min_delay, max_delay)
# FIND
p1, = host.plot(time_list, delay_list, label="Delay")
#p1, = host.plot(stat_time_list, stat_delay_small_list, label="Delay")

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
#DrawLine(time_list, delay_list, ylabel="Delay", yMin = min_delay, yMax = max_delay)
host.legend()
show()
#savefig(png_name)
