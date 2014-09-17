import os
import subprocess
import sys
import threading
import time
import signal
import platform

# argv[0]: this file path
# argv[1]: target file
# argv[2]: timeout
# argv[3: ]: argv for target file argv[1]

    
def kill_all_subprocess(pid):
    PLATFORM_SYSTEM = platform.system()
    if PLATFORM_SYSTEM == "Windows":
        subprocess.Popen("taskkill /T /F /PID " + str(pid))
    elif PLATFORM_SYSTEM == "Linux":
        os.killpg(pid, signal.SIGINT)

def timeout_thread_callback(cond, timeout, subp):
    cond.acquire()
    cond.wait(timeout)
    cond.release()
    if subp.poll() is None:
        kill_all_subprocess(subp.pid)

def start_timeout_thread(cond, timeout, subp):
    sub_thread = threading.Thread(target=timeout_thread_callback, args=(cond, timeout, subp))
    sub_thread.start()
    return sub_thread
    
def start_process_background(timeout):
    cur_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    target_file_name = sys.argv[1]
    target_file = cur_dir + os.sep + target_file_name

    # open sub process
    cmd_line = 'python ' + target_file + ' ' + ' '.join(sys.argv[3:])
    print cmd_line
    subp = subprocess.Popen(cmd_line.split(' '))
    # acquire condition
    cond = threading.Condition()
    # start timeout thread which'll kill process
    timeout_thread = start_timeout_thread(cond, timeout, subp)
    # wait for process to end/killed by timeout thread
    exit_status = subp.wait()
    
    if timeout_thread.is_alive():
        cond.acquire()
        cond.notify()
        cond.release()
        timeout_thread.join()
    cond = None
    
    if exit_status != 0:
        print "Process is terminated due to timeout:" + str(exit_status)
    else:
        print "Process ends successfully"
        
# sys.argv = python abs(start_bgp.py) args
print sys.argv
if len(sys.argv) < 3:
    exit(0)
start_process_background(int(sys.argv[2]))
