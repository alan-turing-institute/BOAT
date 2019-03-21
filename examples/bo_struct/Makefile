CC=g++
CFLAGS=-Wall -fexceptions -std=c++14 -O3 -fopenmp -g
BOAT_DIR=./../../
LIBS= -lboat -lpthread -lblas -lnlopt -lm -lboost_serialization -lboost_system -lboost_coroutine -I $(EIGEN_DIR) -I /usr/local/include -L /usr/local/lib

bo_naive_opti: bo_struct_opti.cpp
	$(CC) -g -o bo_struct_opti $(CFLAGS) -I$(BOAT_DIR)/include/ bo_struct_opti.cpp -L$(BOAT_DIR)/build $(LIBS)

clean:
	rm -f bo_struct_opti
