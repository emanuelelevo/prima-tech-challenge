import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_eks as eks
import pulumi_kubernetes as k8s

def create_eks(context, pulumi_config):

    cluster_name = pulumi_config["cluster_name"]
    min_cluster_size = pulumi_config["min_cluster_size"]
    max_cluster_size = pulumi_config["max_cluster_size"]
    desired_cluster_size = pulumi_config["desired_cluster_size"]
    eks_node_instance_type = pulumi_config["eks_node_instance_type"]
    vpc_network_cidr = pulumi_config["vpc_network_cidr"]

    tags = {
        f"kubernetes.io/cluster/{cluster_name}": "owned"
    }

    eks_vpc = awsx.ec2.Vpc("eks-vpc",
        enable_dns_hostnames=True,
        cidr_block=vpc_network_cidr,
        tags=tags,
        subnet_strategy=awsx.ec2.SubnetAllocationStrategy.AUTO,
        subnet_specs=[
            awsx.ec2.SubnetSpecArgs(
                cidr_mask=24,
                type=awsx.ec2.SubnetType.PUBLIC,
                tags={**tags, "kubernetes.io/role/elb": "1"}
            ),
            awsx.ec2.SubnetSpecArgs(
                cidr_mask=24,
                type=awsx.ec2.SubnetType.PRIVATE,
                tags={**tags, "kubernetes.io/role/internal-elb": "1"}
            ),
        ]    
    )

    eks_cluster = eks.Cluster("eks-cluster",
        name=cluster_name,
        vpc_id=eks_vpc.vpc_id,
        public_subnet_ids=eks_vpc.public_subnet_ids,
        private_subnet_ids=eks_vpc.private_subnet_ids,
        create_oidc_provider=True,
        instance_type=eks_node_instance_type,
        desired_capacity=desired_cluster_size,
        min_size=min_cluster_size,
        max_size=max_cluster_size,
        opts=pulumi.ResourceOptions(depends_on=[eks_vpc])
    )

    aws_account_id = aws.get_caller_identity().account_id
    eks_provider = k8s.Provider("eks-provider", kubeconfig=eks_cluster.kubeconfig)
    oidc_provider_url = eks_cluster.core.oidc_provider.url 

    metrics_server = k8s.yaml.ConfigFile("metrics-server",
        file="support/metrics-server.yaml",
        opts=pulumi.ResourceOptions(provider=eks_provider)
    )

    with open('iam/eks_lb_controller_policy.json', 'r') as file:
        eks_lb_controller_policy_file = file.read()

    eks_lb_controller_policy = aws.iam.Policy("AmazonEKSLoadBalancerControllerIAMPolicy",
        policy=eks_lb_controller_policy_file
    )

    with open('iam/eks_oidc_role_trust_policy.json', 'r') as file:
        eks_oidc_role_trust_policy_file = file.read()

    eks_lb_oidc_role_trust_policy = pulumi.Output.all(
        aws_account_id, oidc_provider_url).apply(
            lambda args: eks_oidc_role_trust_policy_file
            .replace("{{AWS_ACCOUNT_ID}}", args[0])
            .replace("{{OIDC_PROVIDER_URL}}", args[1])
            .replace("{{NAMESPACE}}", "kube-system")
            .replace("{{SA_NAME}}", "aws-load-balancer-controller")
    )

    eks_lb_service_account_role = aws.iam.Role(
        "AmazonEKSLoadBalancerControllerRole",
        assume_role_policy=eks_lb_oidc_role_trust_policy,
    )

    eks_lb_role_policy_attachment = aws.iam.RolePolicyAttachment("AmazonEKSLoadBalancerControllerRolePolicyAttachment",
        role=eks_lb_service_account_role.name,
        policy_arn=eks_lb_controller_policy.arn,
    )

    eks_lb_service_account = k8s.core.v1.ServiceAccount("aws-load-balancer-controller",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name="aws-load-balancer-controller",
            namespace="kube-system",
            annotations={
                "eks.amazonaws.com/role-arn": eks_lb_service_account_role.arn
            }
        ),
        opts=pulumi.ResourceOptions(provider=eks_provider)
    )

    helm_lb_controller = k8s.helm.v3.Release(
        "aws-load-balancer-controller",
        k8s.helm.v3.ReleaseArgs(
            name="aws-load-balancer-controller",
            chart="charts/aws-load-balancer-controller",
            version="1.8.1",
            namespace=eks_lb_service_account.metadata.namespace,
            values={
                "clusterName": cluster_name,
                "serviceAccount": {
                    "create": False,
                    "name": eks_lb_service_account.metadata.name
                }
            }
        ),
        opts=pulumi.ResourceOptions(
            provider=eks_provider, 
            depends_on=[context["acm_certificate"]]
        )
    )

    pulumi.export("cluster_name", eks_cluster.name)
    pulumi.export("lb_service_account_name", eks_lb_service_account.metadata.name)
    pulumi.export("kubeconfig", eks_cluster.kubeconfig)
    pulumi.export("vpc_id", eks_vpc.vpc_id)

    context["eks"] = {
        "provider": eks_provider,
        "helm_lb_controller": helm_lb_controller,
        "oidc_provider_url": oidc_provider_url,
    }
