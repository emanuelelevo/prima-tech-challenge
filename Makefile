.PHONY: localdev address app-docker-build app-docker-run app-docker-localstack-run kubeconfig

container_tag=elevorin-prima-test:latest

# Default values
AWS_REGION ?= eu-north-1
DYNAMODB_TABLE ?= my-table
S3_BUCKET ?= my-bucket
AWS_ENDPOINT_URL ?= http://192.168.0.2:4566

localdev:
	@pulumi stack init localdev \
	&& cp .Pulumi.localdev.yaml Pulumi.localdev.yaml \
	&& pulumi stack select localdev

address:
	@bash support/get-address.sh

app-docker-build:
	@docker build -t ${container_tag} ./apps/flask-app

app-docker-run:
	@docker run --rm -p 5000:5000 -v ~/.aws:/root/.aws \
	-e AWS_REGION=${AWS_REGION} \
	-e DYNAMODB_TABLE=${DYNAMODB_TABLE} \
	-e S3_BUCKET=${S3_BUCKET} \
	-e LOG_LEVEL=${LOG_LEVEL} \
	${container_tag}

app-docker-localstack-run:
	@docker run --rm -p 5000:5000 \
	-e AWS_ACCESS_KEY_ID=test \
	-e AWS_SECRET_ACCESS_KEY=test \
	-e AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL} \
	-e AWS_REGION=${AWS_REGION} \
	-e DYNAMODB_TABLE=${DYNAMODB_TABLE} \
	-e S3_BUCKET=${S3_BUCKET} \
	-e LOG_LEVEL=${LOG_LEVEL} \
	${container_tag}

kubeconfig:
	@pulumi stack --show-name \
	&& pulumi stack output kubeconfig > /tmp/elevorin-kubeconfig \
	&& chmod 600 /tmp/elevorin-kubeconfig \
	&& echo "export KUBECONFIG=/tmp/elevorin-kubeconfig"
