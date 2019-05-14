RAWVERSION = $(filter-out __version__ = , $(shell grep __version__ seedling/__init__.py))
VERSION = $(strip $(shell echo $(RAWVERSION)))
PACKAGE = seedling
REGISTRY = 467892444047.dkr.ecr.us-west-2.amazonaws.com/caltech-imss-ads

# This .PHONY directive tells make that it should not care about any files/directories whose names match our make
# command's names. If this were not here, make would claim "'build' is up to date!" if there were a file/folder called
# 'build' in the root that has an old timestamp.
.PHONY: bootstrap clean build force-build tag pull push dev dev-detached

#======================================================================

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm *.xml pylint.out
	find . -name "*.pyc" -exec rm '{}' ';'

version:
	@echo ${VERSION}

image_name:
	@echo ${REGISTRY}/${PACKAGE}:${VERSION}

build:
	# This mkdir has to be here because the Dockerfile expects it
	docker build -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	# Delete dangling container images to help prevent disk bloat.
	docker image prune -f

force-build:
	# This mkdir has to be here because the Dockerfile expects it
	docker build -t ${PACKAGE}:${VERSION} . --no-cache
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	# Delete dangling container images to help prevent disk bloat.
	docker image prune -f

tag:
	docker tag ${PACKAGE}:${VERSION} ${REGISTRY}/${PACKAGE}:${VERSION}
	docker tag ${PACKAGE}:latest ${REGISTRY}/${PACKAGE}:latest

pull:
	docker pull ${REGISTRY}/${PACKAGE}:${VERSION}

push: tag
	docker push ${REGISTRY}/${PACKAGE}:${VERSION}

dev:
	docker-compose up

dev-detached:
	docker-compose up -d

docker-clean:
	docker stop $(shell docker ps -a -q)
	docker rm $(shell docker ps -a -q)

docker-destroy-db:
	rm -Rf sql/docker/mysql-data/

docker-destroy: docker-clean docker-destroy-db
	docker rmi -f $(shell docker images -q | uniq)
	docker image prune -f; docker volume prune -f; docker container prune -f

test: build
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit

ctags:
	# This sets up the ./tags file for vim that includes all packages in the virtualenv
	# plus our own code
	ctags -R --fields=+l --languages=python --python-kinds=-iv -f ./tags ./ `python -c "import os, sys; print(' '.join('{}'.format(d) for d in sys.path if os.path.isdir(d)))"`

