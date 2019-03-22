.PHONY: pull build run clean push

pull:
	docker pull turingboat/boat:dev

build:
	docker build . -f Dockerfile -t turingboat/boat:dev

run:
	docker run -it turingboat/boat:dev

clean:
	docker image rm turingboat/boat:dev

push:
	docker push turingboat/boat:dev