.PHONY: pull build run clean push base

ifndef branch
n_branch = develop
else
n_branch = $(branch)
endif

all:
	@echo $(n_branch)

pull:
	docker pull turingboat/boat:$(n_branch)

build:
	docker build . -f Dockerfile -t turingboat/boat:$(n_branch)

base:
	docker build . -f Dockerfile.base -t turingboat/boat_base

run:
	docker run -it turingboat/boat:$(n_branch)

clean:
	docker image rm turingboat/boat:$(n_branch)

push:
	docker push turingboat/boat:$(n_branch)