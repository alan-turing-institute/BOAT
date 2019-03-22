FROM turingboat/boat_base as boat

# installing BOAT
WORKDIR "/"

RUN git clone --branch bo_simulator https://github.com/alan-turing-institute/BOAT.git
RUN mkdir BOAT/build
WORKDIR "/BOAT/build/"
RUN cmake ../src; make

# WORKDIR "/BOAT/examples/branin_hoo/"
# CMD ["make"]

WORKDIR "/"
