#!/bin/bash 

cd ../../build/; rm -rf *; cmake ../src/; make; cd ../examples/bo_struct/; make;