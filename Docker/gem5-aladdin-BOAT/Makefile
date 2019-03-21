.PHONY: build run clean# push

build:
	docker build . -f Dockerfile -t gem5-aladdin-boat:dev

run:
	docker run -it --rm \
		--mount source=gem5-aladdin-boat-workspace,target=/workspace \
		gem5-aladdin-boat:dev

clean:
	docker image rm gem5-aladdin-boat
  	# docker volume rm gem5-aladdin-boat-workspace

# push:
# 	docker push tomaslaz/gem5-aladdin-boat:dev