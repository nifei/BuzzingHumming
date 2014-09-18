import range
import statpcap
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from pylab import *
import time
import re
png_name = 'delay1.png'
merge = statpcap.StatPcap
min_delay, max_delay = None, None
time_list = list()
delay_list = list()
time_loss_list = list()
loss_list = list()
input_pcap = sys.argv[1]
output_pcap = sys.argv[2]

time_before = time.time()
counter = 0
for item in merge(output_pcap, input_pcap, '192.168.91.253', '192.168.91.64'):
    if 'delay' in item.keys():
        time_list.append(item['out'])
        delay_list.append(item['delay'])
        min_delay, max_delay = range.calib_range(min_delay, max_delay, item['delay'])
    elif 'loss' in item.keys():
        time_loss_list.append(item['out'])
        loss_list.append(item['loss'])
    #print item
#    counter = counter + 1
#    if counter >= 100:
#        print '100'
#        counter = 0

time_after = time.time()
dur = time_after - time_before

min_delay, max_delay = range.extend_range(min_delay, max_delay)
print 'delay range:', min_delay, max_delay
print 'time range:', time_list[-1] - time_list[0]
print 'sample count:', len(time_list)
print 'complexity:', dur

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
DrawLine(time_loss_list, loss_list, ylabel="Loss", yMin = 0, yMax = 1.2)
host.legend()
show()
#savefig(png_name)
