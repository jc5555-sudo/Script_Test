#!/bin/bash

set -e   # stop if any command fails

python3 /home/inf25/work/fc_script/fc_log_reporting_script/script_python.py

python3 /home/inf25/work/fc_script/fc_log_reporting_script/script_python2.py

python3 /home/inf25/work/fc_script/fc_log_reporting_script/script_python3.py

rm -rf fc_command.log
rm -rf fc_output.txt
