VERSION = 0.1.0

PACKAGE = seedling

# FIXME: set to actual docker registry
DOCKER_REGISTRY = cmalek

# This .PHONY directive tells make that it should not care about any files/directories whose
# names match our make commands' names. If this were not here, make would claim "'build' is up to date!" if there were
# a file/folder called 'build' in the root that has an old timestamp.
.PHONY: aws-login clean version image_name dist build force-build tag push dev dev-detached devup devdown logall log exec restart release prep test docker-clean docker-destroy-db docker-destroy list
#======================================================================

aws-login:
	@$(shell aws ecr get-login --region us-west-2 --no-include-email)

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm
	find . -name "*.pyc" -exec rm '{}' ';'

version:
	@echo $(VERSION)

image_name:
	@echo ${DOCKER_REGISTRY}/${PACKAGE}:${VERSION}

dist: clean
	@python setup.py sdist

build:
	docker build -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	docker image prune -f

force-build:
	docker build --no-cache -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	docker image prune -f

tag:
	docker tag ${PACKAGE}:${VERSION} ${DOCKER_REGISTRY}/${PACKAGE}:${VERSION}
	docker tag ${PACKAGE}:latest ${DOCKER_REGISTRY}/${PACKAGE}:latest

push: tag aws-login
	docker push ${DOCKER_REGISTRY}/${PACKAGE}

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-detached:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

devup: dev-detached

devdown:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

logall:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

log:
	docker logs -f seedling

exec:
	docker exec -it seedling /bin/bash

restart:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart seedling

release:
	@bin/release.sh

prep:
	@test -e /etc/context.d || mkdir -p /etc/context.d
	@if [[ -e /etc/context.d/seedling.env ]]; then \
	    echo '/etc/context.d/seedling.env exists.'; \
	else \
		cp etc/environment.txt /etc/context.d/seedling.env;  \
	    echo "Installed etc/environment.txt as /etc/context.d/seedling.env";  \
	fi
	@echo
	@grep -n -e "^[^#].*=__\(.*\)__" /etc/context.d/seedling.env > /dev/null 2>&1 && (echo "Replace these placeholders in /etc/context.d/seedling.env:"; grep -n -e "^[^#].*=__\(.*\)__" /etc/context.d/seedling.env) || echo "/etc/context.d/seedling.env has no placeholders to replace."

test:
	# We have to do this because in docker-compose.yml, we've referenced our container image as
	# seedling:latest, but if we're in CodePipeline, we don't have that image yet
	# If CODEBUILD_BUILD_ID exists in our shell environment, we know we're in the pipeline
	# Copy in the config files -- docker-compose expects them
	test -e /etc/context.d || mkdir -p /etc/context.d
	test -e /etc/context.d/seedling.env || cp etc/environment.txt /etc/context.d/seedling.env
	# Bring up the whole stack
	docker-compose up -d
	# Run the tests
	docker exec -ti seedling /bin/bash -c "export TESTING=True && ./manage.py test"
	# Extract the test report
	mkdir -p reports
	docker cp seedling:/app/results.xml reports/results.xml
	# Shut down the stack
	docker-compose down

docker-clean:
	docker stop $(shell docker ps -a -q)
	docker rm $(shell docker ps -a -q)

docker-destroy-db:
	rm -Rf sql/docker/mysql-data/

docker-destroy: docker-clean docker-destroy-db
	docker rmi -f $(shell docker images -q | uniq)
	docker image prune -f; docker volume prune -f; docker container prune -f

list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs
