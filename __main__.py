import pulumi
import pulumi_aws as aws
from resources.s3 import create_s3
from resources.dynamodb import create_table
from resources.acm import create_cert
from resources.eks import create_eks
from resources.helm import create_helm
from resources.oidc_sa import create_oidc_sa


config = pulumi.Config()
pulumi_config = {
    "aws_region": config.get("aws:region", "eu-north-1"),
    "bucket_name": config.get("bucket-name", "elevorin-prima-test"),
    "table_name": config.get("table-name", "elevorin-prima-test"),
    "flask_app_namespace": config.get("flask-app-namespace", "default"),
    "flask_app_sa_name": config.get("flask-app-sa-name", "flask-app"),
    "cluster_name": config.get("cluster-name", "elevorin-prima-test"),
    "min_cluster_size": config.get_int("min-cluster-size", 2),
    "max_cluster_size": config.get_int("max-cluster-size", 6),
    "desired_cluster_size": config.get_int("desired-cluster-size", 2),
    "eks_node_instance_type": config.get("eks-node-instance-type", "t3.medium"),
    "vpc_network_cidr": config.get("vpc-network-cidr", "10.0.0.0/16"),
    "localstack_url": config.get("localstack-url", "http://192.168.0.2:4566"),
}

context = {
    "aws_account": aws.get_caller_identity(),
}

create_table(context, pulumi_config)
create_s3(context, pulumi_config)

# Hack for localstack and minikube
stack_name = pulumi.get_stack()
if stack_name != "localdev":
    create_cert(context, pulumi_config)
    create_eks(context, pulumi_config)
    create_oidc_sa(context, pulumi_config)
else:
    context["eks"] = "localdev"

create_helm(context, pulumi_config)
