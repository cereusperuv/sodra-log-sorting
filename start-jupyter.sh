#!/bin/bash

# Local port and notebook password
. configs/docker.config

# Change dir and run server
cd notebooks
nohup jupyter notebook --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token=$pwd > jupyter-server.log 2>&1 &
cd ..

# Output string
echo
echo "Click this link or copy into browser:"
echo
echo "   http://localhost:$local_port/?token=$notebook_pwd"
echo
