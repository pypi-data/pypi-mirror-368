REGISTRY?=r.intra.logilab.fr/intranet/fresh
VERSION?=$(shell hg log -r . -T "{sub(':.*', '', '{latesttag}')}{sub('^-0-.*', '', '-{latesttagdistance}-hg{shortest(node, 7)}')}\n")
IMAGE?=$(REGISTRY):$(VERSION)
PORT?=8080
DOCKER_ARGS?=$(shell test -e .env && echo --env-file .env) -p $(PORT):8080 -v /var/run/postgresql:/var/run/postgresql -e CW_DB_USER=$(shell id -nu)
NAMESPACE=intranet

all: build

build:
	docker build --pull -t $(IMAGE) .

push: build
	docker push $(IMAGE)
	docker tag $(IMAGE) $(REGISTRY):latest
	docker push $(REGISTRY):latest

run: build
	docker run $(DOCKER_ARGS) --rm -it $(IMAGE)

dev: build
	docker run --rm -it $(DOCKER_ARGS) -v `pwd`:/src $(IMAGE) bash

deploy: push
	sed "s@r.intra.logilab.fr/intranet/fresh@$(IMAGE)@" deploy/deployment.yaml | kubectl -n $(NAMESPACE) apply -f -
	kubectl -n $(NAMESPACE) rollout restart deployment/fresh deployment/fresh-scheduler
	@echo "wait at max 3 minutes for deployment to be UP"
	kubectl -n $(NAMESPACE) rollout status --timeout=180s deployment/fresh
	kubectl -n $(NAMESPACE) rollout status --timeout=180s deployment/fresh-scheduler

.PHONY: all build push run dev deploy
