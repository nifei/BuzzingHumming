import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from pylab import *
import re

log_file_path='./'
in_file = log_file_path + sys.argv[1]
out_file = log_file_path + sys.argv[2]
dest_png_path='./buzzing.png'
time_unit = 1000000
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

def ReadFile(log_file_path):
    with open(log_file_path, 'r') as file:
        for line in file:
            row = [int(value) for value in line.split(' ')]
            yield row
        file.close()

seq_list = list()
time_list = list()
delay_list = list()

min_delay, max_delay=None, None

Out = ReadFile(out_file)
In = ReadFile(in_file)

row_s = In.next()
seq_s = int(row_s[1])
time_in = int(row_s[0])
min_seq_in = seq_s

# stat every sample_interval, stat previous sample_count sample
config_sample_interval = 1000000 # micro second
config_sample_count = 10
config_sample_packet = 100 # calculate packet loss in recent config_sample_packet

stat_delay_list = list()
stat_loss_list  =list()
stat_time_list = list()

stat_delay_small_list = list()
stat_loss_small_list = list()

delay_count_small = 0
sample_count_big = 0
sample_delay_sum_big = 0
sample_delay_sum_small = 0

sample_loss_small = 0 # packet loss count in every config_sample_interval

disorder_seq_index_client = {}
disorder_seq_time_client = {}

disorder_seq_index_server = {}
disorder_seq_time_server = {}

last_time = None

def log(message):
    pass
#    if (seq <= 2000):
#         print message

def log_dict():
     log('client:')
     log(disorder_seq_time_client)
     log('server:')
     log(disorder_seq_time_server)


def update_seq_s_in_client_log():
    if seq_s in disorder_seq_time_client.keys():
        log(str(seq_s) + ' in disorder_seq_time_client')
        server_time = time_in
        client_time = disorder_seq_time_client[seq_s]
        delay_ = server_time - client_time 
        index_ = disorder_seq_index_client[seq_s]
#        log('update delay_list:' + str(index_) )
        delay_list[index_] = delay_
#        log('pop ' + str(seq_s) + ' in disorder_seq_time_client')
        disorder_seq_time_client.pop(seq_s, None)
 
try:
    for row in Out:
        if len(row) < 2:
            continue
        seq = int(row[1])
        if seq < min_seq_in:
            continue
        time_out = int(row[0])
        if seq_s == seq:
            delay = time_in - time_out
            row_s = In.next()
            seq_s = int(row_s[1])
            time_in = int(row_s[0])
            if seq in disorder_seq_time_server.keys():
#                log(str(seq) + ' in disorder_seq_time_server, pop it')
                disorder_seq_time_server.pop(seq, None)
        elif int(seq_s) > int(seq): 
#            log( 'server '+ str(seq_s) + '>' + ' client ' + str(seq))
            if (len(delay_list) > 0):
                delay = delay_list[-1]
#                log( 'fake delay:' + str(seq))
                disorder_seq_index_client[seq] = len(seq_list)
                disorder_seq_time_client[seq] = time_out
                disorder_seq_time_server[seq_s] = time_in
#                log_dict()
            else:
                continue
        else:
            # disorder not handled!
            # seq_s < seq
#            log('server ' + str(seq_s) + '<' + ' client ' + str(seq))
#            log_dict() 
            update_seq_s_in_client_log()
            if seq in disorder_seq_time_server.keys():
#                log(str(seq) + ' in disorder_seq_time_server')
                server_time = disorder_seq_time_server[seq]
                client_time = time_out
                delay = server_time - client_time 
                disorder_seq_time_server.pop(seq, None)
#                log('find delay:' + str(seq))
            else:
            # seq_s < seq
            # need to read next until find seq_s = seq
                while seq_s < seq:
                    row_s = In.next()
                    seq_s = int(row_s[1])
                    time_in = int(row_s[0])
                    update_seq_s_in_client_log()
                delay = time_in - time_out
             
            row_s = In.next()
            seq_s = int(row_s[1])
            time_in = int(row_s[0])

        if last_time == None:
            last_time = time_in

        min_delay, max_delay = calib_range(min_delay, max_delay, delay)
        seq_list.append(seq)
        time_list.append(time_in/time_unit)
        delay_list.append(delay)
          
        if time_in - last_time >= config_sample_interval:
            stat_time_list.append(int(last_time/time_unit))
            average_delay_small = sample_delay_sum_small/delay_count_small
            stat_delay_small_list.append(average_delay_small)
            
            sample_delay_sum_big += average_delay_small
            sample_count_big = sample_count_big + 1
            # packet loss
            # update disorder_seq_time_client, remove seq 100 before
            log(str(seq))
            disorder_seq_time_client = {key:disorder_seq_time_client[key] for key in disorder_seq_time_client.keys() if key > seq - config_sample_packet}
            log_dict()
            packet_loss = 1- float(config_sample_packet - len(disorder_seq_time_client))/float(config_sample_packet)
            stat_loss_small_list.append(packet_loss)

            if sample_count_big > config_sample_count:
                toSub = stat_delay_small_list[-1 - config_sample_count]
                sample_delay_sum_big -= toSub
                sample_count_big = sample_count_big - 1
            average_delay = float(sample_delay_sum_big)/float(sample_count_big)
            stat_delay_list.append(average_delay)

            sample_delay_sum_small = delay
            delay_count_small = 1
            last_time = time_in
        else:
            sample_delay_sum_small = sample_delay_sum_small + delay
            delay_count_small = delay_count_small + 1
#        log_dict()
            
except StopIteration:
    print('Stop Iteration')
    pass

min_delay, max_delay = extend_range(min_delay, max_delay)


clf()
host = host_subplot(111, axes_class=AA.Axes)
plt.subplots_adjust(right=0.75)
host.set_xlabel("time")
host.set_ylabel("Delay")
host.set_ylim(min_delay, max_delay)
# FIND
p1, = host.plot(stat_time_list, stat_delay_list, label="Delay")
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
DrawLine(stat_time_list, stat_loss_small_list, "Loss", -0.1, 1.1)

if len(sys.argv) > 3:
    min_http, max_http = None, None
    # start wget line #
    wget_file = log_file_path + sys.argv[3]
    Http = ReadFile(wget_file)
    http_time_list = list()
    http_delta_list = list()
    for row in Http:
        http_time_list.append(row[0])
        http_time = row[1]
        min_http, max_http = calib_range(min_http, max_http, http_time)
        http_delta_list.append(http_time)
    min_http, max_http = extend_range(min_http, max_http)
    DrawLine(http_time_list, http_delta_list, "Http", min_http, max_http)

host.legend()
#show()
savefig(dest_png_path)
