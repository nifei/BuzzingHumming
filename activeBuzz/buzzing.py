__author__ = 'test'
import subprocess
import sys
import os
import time
import datetime
import signal
import traceback

is_exited = False

def on_sigint(*args, **kwargs):
    global is_exited
    is_exited = True

signal.signal(signal.SIGINT, on_sigint)

log_dir = './'
packet_log_file_name = sys.argv[1]+'.buzz.log'
wget_log_file_name=sys.argv[1]+'.wget.log'
arg = sys.argv[2]
ip = sys.argv[3]
port = sys.argv[4]
cmd_line = "BuzzTest.exe " + arg + " " + ip + " -p " + port + " -u"

packet_log_file = log_dir + os.sep + packet_log_file_name
wget_log_file = log_dir + os.sep + wget_log_file_name

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
cur_dir = os.getcwd()
log = open(packet_log_file, 'w+')
os.chdir(script_dir)

cmd_line = cmd_line.split(' ')
subp = subprocess.Popen(cmd_line, stdout=log, stderr=log, shell=True)
#subp.communicate()

if arg=='-in': # input
    wget_cmd_line = 'wget -qO baidu http://192.168.91.144:8987/dependence/test/baidu'
    wget_log = open(wget_log_file, 'w')
    epoch_current_time = lambda: int(time.time() * 1000000)
    time.sleep(5)
    while not is_exited:
        try:
            time.sleep(2)
            #time_before = datetime.datetime.now()
            time_before = epoch_current_time()
            subprocess.call(wget_cmd_line, shell=True)
            file_size = 82389
            #time_after = datetime.datetime.now()
            time_after = epoch_current_time()
            time_delta = time_after - time_before
            if wget_log.tell():
                wget_log.write('\n')
            wget_log.write('%d %d %d'%(time_before, time_delta, file_size))
            wget_log.flush()
        except IOError:
            pass
    print ('byby while')
    wget_log.close()
else:
    subp.communicate()
os.chdir(cur_dir)