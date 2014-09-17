import os
import subprocess
import sys
import inspect
import threading
    
def get_script_dir():
    path = inspect.getabsfile(get_script_dir)
    return os.path.dirname(path)

path = get_script_dir()
target_file_name = 'start_bgp.py'
target_file = path + os.sep + target_file_name

if len(sys.argv) > 1:
    argv = sys.argv[1: ]
else:
    argv = []

# argv = xdt/task.py process.py args
# cmd_line = python abs(start_bgp.py) args
cmd_line = 'python ' + target_file + ' ' + ' '.join(argv)
subprocess.Popen(cmd_line.split(' '))
