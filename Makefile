RAWVERSION = $(filter-out __version__ = , $(shell grep __version__ multitenant/__init__.py))
VERSION = $(strip $(shell echo $(RAWVERSION)))
PACKAGE = caltechsites
REGISTRY = 467892444047.dkr.ecr.us-west-2.amazonaws.com/caltech-imss-ads

# This .PHONY directive tells make that it should not care about any files/directories whose
# names match our make command's names. If this were not here, make would claim "'build' is up to date!" if there were
# a file/folder called 'build' in the root that has an old timestamp.
.PHONY: aws-login aws-login-old bootstrap clean build force-build codebuild tag pull push dev test

#======================================================================

aws-login:
	@exec aws ecr get-login --region us-west-2 --no-include-email

aws-login-old:
	@exec aws ecr get-login --region us-west-2

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm *.xml pylint.out
	find . -name "*.pyc" -exec rm '{}' ';'

version:
	@echo ${VERSION}

image_name:
	@echo ${REGISTRY}/${PACKAGE}:${VERSION}

build:
	# This mkdir has to be here because the Dockerfile expects it
	mkdir -p dependencies
	docker build -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	# Delete dangling container images to help prevent disk bloat.
	docker image prune -f
	rm -rf dependencies

force-build:
	# This mkdir has to be here because the Dockerfile expects it
	mkdir -p dependencies
	docker build -t ${PACKAGE}:${VERSION} . --no-cache
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	# Delete dangling container images to help prevent disk bloat.
	docker image prune -f
	rm -rf dependencies

codebuild:
	bin/pre-get-dependencies.sh requirements.txt && mv requirements.txt.new requirements.txt
	docker build -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	rm -rf dependencies

tag:
	docker tag ${PACKAGE}:${VERSION} ${REGISTRY}/${PACKAGE}:${VERSION}
	docker tag ${PACKAGE}:latest ${REGISTRY}/${PACKAGE}:latest

pull:
	docker pull ${DOCKER_REGISTRY}/${PACKAGE}:${VERSION}

push: tag
	docker push ${REGISTRY}/${PACKAGE}:${VERSION}

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-detached:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

elastic:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d elastic

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

mysql-login:
	mysql -u multitenant_u -p -h db-multitenant multitenant

update-test-service: aws-login configure-python
	ve/bin/python bin/deploy.py update test $(VERSION)

update-prod-service: aws-login configure-python
	ve/bin/python bin/deploy.py update prod $$(ve/bin/python bin/deploy.py image_version test)

pipeline-create:
	aws codebuild create-project --cli-input-json file://codepipeline/codebuild-docker.json
	aws codebuild create-project --cli-input-json file://codepipeline/codebuild-test-deploy.json
	aws codebuild create-project --cli-input-json file://codepipeline/codebuild-divisions-test-deploy.json
	aws codebuild create-project --cli-input-json file://codepipeline/codebuild-test-osc-web-deploy.json
	aws codepipeline create-pipeline --cli-input-json file://codepipeline/codepipeline-test.json
	aws codebuild create-project --cli-input-json file://codepipeline/codebuild-caltechsites-prod-deploy.json
	aws codepipeline create-pipeline --cli-input-json file://codepipeline/codepipeline-caltechsites-prod.json
	aws codebuild create-project --cli-input-json file://codepipeline/codebuild-oscweb-prod-deploy.json
	aws codepipeline create-pipeline --cli-input-json file://codepipeline/codepipeline-oscweb-prod.json

pipeline-update-projects:
	aws codebuild update-project --cli-input-json file://codepipeline/codebuild-docker.json
	aws codebuild update-project --cli-input-json file://codepipeline/codebuild-test-deploy.json
	aws codebuild update-project --cli-input-json file://codepipeline/codebuild-divisions-test-deploy.json
	aws codebuild update-project --cli-input-json file://codepipeline/codebuild-test-osc-web-deploy.json
	aws codebuild update-project --cli-input-json file://codepipeline/codebuild-caltechsites-prod-deploy.json
	aws codebuild update-project --cli-input-json file://codepipeline/codebuild-oscweb-prod-deploy.json

pipeline-update: pipeline-update-projects
	aws codepipeline update-pipeline --cli-input-json file://codepipeline/codepipeline-test.json
	aws codepipeline update-pipeline --cli-input-json file://codepipeline/codepipeline-caltechsites-prod.json
	aws codepipeline update-pipeline --cli-input-json file://codepipeline/codepipeline-oscweb-prod.json

ctags:
	# This sets up the ./tags file for vim that includes all packages in the virtualenv
	# plus our own code
	ctags -R --fields=+l --languages=python --python-kinds=-iv -f ./tags ./ `python -c "import os, sys; print(' '.join('{}'.format(d) for d in sys.path if os.path.isdir(d)))"`

