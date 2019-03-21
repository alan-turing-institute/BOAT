FROM xyzsam/gem5-aladdin
LABEL maintainer="Tomas Lazauskas"

# removing orginal gem5-aladdin repository
RUN rm -rf gem5-aladdin

# cloning gem5-aladdin-boat develop branch
RUN git clone https://github.com/alan-turing-institute/gem5-aladdin-boat && \
    cd gem5-aladdin-boat && \
    git fetch && \
    git checkout develop && \
    git submodule init && \
    git submodule update

# updating the enviromental parameter
ENV ALADDIN_HOME /workspace/gem5-aladdin-boat/src/aladdin

# Install BOAT dependencies.
RUN apt-get install -y \
      g++ 
    #   \
    #   libblas-dev \
    #   liblapack-dev \


# installing dependencies: eigen
WORKDIR "/var/tmp"
RUN git clone https://github.com/eigenteam/eigen-git-mirror
WORKDIR "/var/tmp/eigen-git-mirror"
RUN mkdir build
WORKDIR "/var/tmp/eigen-git-mirror/build"
RUN cmake ..; make; make install

#ENV PATH="/usr/local/include/eigen3:${PATH}"
ENV EIGEN_DIR="/usr/local/include/eigen3"
ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"

# installing dependencies: nlopt
WORKDIR "/var/tmp"
RUN git clone git://github.com/stevengj/nlopt
WORKDIR "/var/tmp/nlopt"
RUN mkdir build
WORKDIR "/var/tmp/nlopt/build"
RUN cmake ..; make; make install

WORKDIR "/workspace/gem5-aladdin-boat/BOAT"
RUN mkdir build
WORKDIR "/workspace/gem5-aladdin-boat/BOAT/build/"
RUN cmake ../src; make


# WORKDIR "/workspace/gem5-aladdin/BOAT"
# RUN git checkout bo_simulator 

# # RUN git clone --branch chk_depend https://github.com/alan-turing-institute/BOAT.git


# ### get wget git etc
# # RUN apt-get update; apt-get -y install 
# # RUN apt-get update; apt-get -y install 
# # RUN apt-get update; apt-get -y install g++
# # RUN apt-get update; apt-get -y install libblas-dev
# # RUN apt-get update; apt-get -y install liblapack-dev
# # RUN apt-get update; apt-get -y install libboost-all-dev

# ENV BOAT_HOME /workspace/gem5-aladdin/BOAT

# WORKDIR /workspace