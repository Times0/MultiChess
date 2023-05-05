CC = g++

SRC_DIR := src
OBJ_DIR := obj
BIN_DIR := bin

SRC := $(wildcard $(SRC_DIR)/*.cpp)
OBJ := $(SRC:$(SRC_DIR)/%.cpp=$(OBJ_DIR)/%.o)

CPPFLAGS := 
CFLAGS   :=
LDFLAGS  := -Llib
LDLIBS   := -lm -pthread



chess: $(filter-out $(OBJ_DIR)/main_client.o $(OBJ_DIR)/main_server.o,$(OBJ)) 	 
	mkdir -p bin
	$(CC) $(LDFLAGS) $(filter-out $(OBJ_DIR)/main_client.o $(OBJ_DIR)/main_server.o,$^) $(LDLIBS) -o $(BIN_DIR)/$@


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
