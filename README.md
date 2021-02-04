# python-ismrmrd-server

This work is forked from work by @kspaceKelvin and intends to be our server interface to integrate with Siemens' platform.

## Goal
The goal is to have a docker container run and start this server to listen for data. Once data is received, it should trigger the correct SubtleApp, run processing and send the output back.

The following things will need to be adapted / added to this repo: 
 - An adapted process function that can be called from the handle
 - Dockerfile to build a docker image that starts this server and packages the correct app (could be done on the app side)
 - A queue system to ensure that only one app job is called at a time
 
 ## Operation
 How this example ismrmrd python server works: 
- Entry point is a shell script (start-fire-python-server.sh) that calls the main.py
- In main: initialize a server and calls server.serve()
- In the server: open a socket to listen and feed it to a handling function (either directly or through a multiprocess)
- Handle: open a connection to receive data from socket  (Option to save data to file )
    - In connection: handler switch decide how to read the data being received (—> Multiple types of data can be read: config file, config text, metadata, image input, etc —> see constants)
- In handle: start a process based on what is received in the config
- The process sends data back through the connection

