CC = g++

SRC_DIR := src
OBJ_DIR := obj
BIN_DIR := bin

SRC := $(wildcard $(SRC_DIR)/*.cpp)
OBJ := $(SRC:$(SRC_DIR)/%.cpp=$(OBJ_DIR)/%.o)

CPPFLAGS := -Iinclude -MMD -MP
CFLAGS   :=
LDFLAGS  := -Llib
LDLIBS   := -lm -pthread



game: $(filter-out $(OBJ_DIR)/main_client.o $(OBJ_DIR)/main_server.o,$(OBJ)) 	 
	mkdir -p bin
	$(CC) $(LDFLAGS) $(filter-out $(OBJ_DIR)/main_client.o $(OBJ_DIR)/main_server.o,$^) $(LDLIBS) -o $(BIN_DIR)/$@

client: $(SRC_DIR)/main_client.cpp
	mkdir -p bin
	g++ $(SRC_DIR)/main_client.cpp -o $(BIN_DIR)/$@

server: $(filter-out $(OBJ_DIR)/main_client.o $(OBJ_DIR)/main.o,$(OBJ)) 	 
	mkdir -p bin
	$(CC) $(LDFLAGS) $(filter-out $(OBJ_DIR)/main_client.o $(OBJ_DIR)/main.o,$^) $(LDLIBS) -o $(BIN_DIR)/$@


#creation .o
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	mkdir -p obj
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@
	
clean:
	@$(RM) -rv $(BIN_DIR) $(OBJ_DIR)

-include $(OBJ:.o=.d)
