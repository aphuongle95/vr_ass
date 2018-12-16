#!/bin/bash

# get directory of script
DIR="$( cd "$( dirname "$0" )" && pwd )"

GUACAMOLE=/opt/guacamole/master
AVANGO=/opt/avango/master


### LD_LIBRARY_PATH ###

# third party libs
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/boost/current/lib:/opt/zmq/current/lib:/opt/Awesomium/lib:/opt/pbr/inst_cb/lib

# schism
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/schism/current/lib/linux_x86

# avango
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$AVANGO/lib

# guacamole
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$GUACAMOLE/lib

# lamure
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/lamure/install/lib


### PYTHONPATH ###
export PYTHONPATH=$AVANGO/lib/python3.5



# run daemon
if [[ $* == *-d* ]]
then
    echo "starting daemon"
    python3 daemon.py

else
	echo "starting daemon && application"

    # run daemon
    python3 ./daemon.py > /dev/null &
    
    # run program
    cd "$DIR" && DISPLAY=:0.0 python3 ./main.py
fi


# kill daemon & application
kill %1
kill %2
