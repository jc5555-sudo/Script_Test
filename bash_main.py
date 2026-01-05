#!/bin/bash

set -e   # stop if any command fails

python3 /home/inf25/work/fc_script/test_local_script/script_python

python3 /home/inf25/work/fc_script/test_local_script/script_python2

python3 /home/inf25/work/fc_script/test_local_script/script_python3

rm -rf fc_command.log
rm -rf fc_output.txt
rm -rf logs_report/*.bak
