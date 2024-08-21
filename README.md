## Prima Tech challenge Senior SRE - July ’24

### Solution Architecture
The awsx module is used for creating a production ready network infrastructure. The cluster scopes different availability zones, private and public subnets. The EKS cluster owns the VPC created by awsx. The EKS cluster leverages OIDC for the deployment service accounts. An AWS Load Balancer Controller is made available for creating Application Load Balancers from the ingress definitions. The metrics-server is made available for enabling HorizontalPodAutoscaler definitions. The EKS cluster may scale its nodes and the flask-app deployment may scale its replicas based on CPU thresholds. (NAT Gatway, CloudFront, Dynamodb DAX are not deployed.)

I've decided to use Pulumi because it's new to me and I want to explore it. However, the approach in this repository is quite unconventional, the Pulumi resources rely on a context dictionary instead of repeatedly fetching data with `.Get*` methods. Moreover, supporting both EKS and Minikube within the same IaC setup doesn't lead to the cleanest code.

### Deploy on AWS
Prerequisites:
- aws cli, with access to an AWS account
- pulumi
- make
- curl

All resources may be deployed with: 
```
pulumi stack init
pulumi up
```
Verify the flask app by fetching the loadbalancer ingress hostname:
```
make address
```
export the provided HOST_ADDRESS on your session and try with curl:
```
curl -X GET ${HOST_ADDRESS}/users
```
```
curl -X POST ${HOST_ADDRESS}/user \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'name=Test User' \
  -F 'email=test-user@elevorin.it' \
  -F 'avatar=@support/test-avatar.png'
```
If needed, the KUBECONFIG may be generated with:
```
make kubeconfig
```

### Deploy on localstack and minikube
Prerequisites:
- localstack cli
- minikube
- make
- curl

Start localstack in host network mode:
```
localstack start --network host
```
Start minikube:
```
minikube start
```
Create the localdev stack with make:
```
make localdev
```
Update the Pulumi.localdev.yaml config localstack-url with your machine ip, e.g.:
```
localstack-url: http://192.168.1.10:4566
```
All resources may be deployed with: 
```
minikube update-context
pulumi up
```
Verify the flask app by fetching the node ip:
```
make address
```
export the provided HOST_ADDRESS on your session and try with curl:
```
curl -X GET ${HOST_ADDRESS}/users
```
```
curl -X POST ${HOST_ADDRESS}/user \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'name=Test User' \
  -F 'email=test-user@elevorin.it' \
  -F 'avatar=@support/test-avatar.png'
```

### Helm
The helm chart releases are also available via helm cli.

The flask-app AWS EKS release may be altered with:
```
pulumi stack output
helm upgrade elevorin-prima-test ./charts/flask-app \
  --set env.AWS_REGION=eu-north-1 \
  --set env.DYNAMODB_TABLE=set-table-name-from-pulumi-output \
  --set env.S3_BUCKET=set-backet-name-from-pulumi-output 
```
The flask-app minikube release may be altered with:
```
pulumi stack select localdev
pulumi stack output
helm upgrade elevorin-prima-test ./charts/flask-app \
  --set serviceAccount.enabled=False \
  --set env.AWS_REGION=eu-north-1 \
  --set env.AWS_ACCESS_KEY_ID=test \
  --set env.AWS_SECRET_ACCESS_KEY=test \
  --set env.AWS_ENDPOINT_URL=http://<set-your-machine-ip>:4566 \
  --set env.DYNAMODB_TABLE=set-table-name-from-pulumi-output \
  --set env.S3_BUCKET=set-backet-name-from-pulumi-output
```
### Docker
The flask-app container may be built with:
```
docker build -t elevorin-prima-test:latest ./apps/flask-app
```
The flask-app container may run using your own AWS credentials:
```
docker run --rm -p 5000:5000 -v ~/.aws:/root/.aws \
  -e AWS_REGION=${AWS_REGION} \
  -e DYNAMODB_TABLE=${DYNAMODB_TABLE} \
  -e S3_BUCKET=${S3_BUCKET} \
  -e LOG_LEVEL=${LOG_LEVEL} \
  ${container_tag}
```
The flask-app container may run using the localstack endpoint:
```
docker run --rm -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=test \
  -e AWS_SECRET_ACCESS_KEY=test \
  -e AWS_ENDPOINT_URL=http://<set-your-machine-ip>:4566 \
  -e AWS_REGION=${AWS_REGION} \
  -e DYNAMODB_TABLE=${DYNAMODB_TABLE} \
  -e S3_BUCKET=${S3_BUCKET} \
  -e LOG_LEVEL=${LOG_LEVEL} \
  ${container_tag}
```
The Makefile has a couple of commands for automating the above, you may consider using an `.env` file by copying `.env-example`. 



