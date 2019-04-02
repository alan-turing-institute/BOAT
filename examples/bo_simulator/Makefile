CC=g++-8
CFLAGS=-Wall -fexceptions -std=c++14 -O3 -fopenmp
BOAT_DIR=./../../
LIBS= -lboat -lpthread -lblas -lnlopt -lm -lboost_serialization -lboost_system -lboost_coroutine -I $(EIGEN_DIR)

bo_simulator: bo_simulator.cpp
	$(CC) -o bo_simulator $(CFLAGS) -I$(BOAT_DIR)/include/ bo_simulator.cpp -L$(BOAT_DIR)/build $(LIBS)

clean:
	rm -f bo_simulator
