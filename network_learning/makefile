CC = g++

CFLAGS = -g -Wall -Werror

all: main

main: client.cpp server.cpp
	mkdir -p bin
	$(CC) $(CFLAGS) -o bin/client client.cpp
	$(CC) $(CFLAGS) -o bin/server server.cpp

clean:
	rm -rf bin


# Path: network_learning/client.cpp