# MultiChess
## Description
Multichess allows you to play chess with your friends on a *local* network. It is composed of a server and a client. The server is written in C and the client in Python.

The server runs by default on ip `127.0.0.1` port `5001`, you can change it with your ip that you can find with the command `ifconfig` and the port you want to use. The client will ask you for the ip and the port of the server. 

## Installation
### Server
To run the server on your machine, just run the following commands :
```bash
cd server
make server
bin/server
```
Note that you can play a basic version of chess in the terminal with the following commands :
```bash
cd server
make chess
bin/chess
```

### Client
To run the client on your machine you need to install the python libraries listed in the requirements.txt file.
```bash
pip install -r requirements.txt
```
Then you can run the client with the following commands :
```bash
cd client
python main.py
```

