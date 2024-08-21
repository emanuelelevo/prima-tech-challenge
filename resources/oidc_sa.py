import pulumi
import pulumi_aws as aws
import pulumi_kubernetes as k8s

def create_oidc_sa(context, pulumi_config):

    aws_account_id = context["aws_account"].account_id
    oidc_provider_url = context["eks"]["oidc_provider_url"]
    flask_app_table_name = context["table"].name
    flask_app_bucket_name = context["bucket"].id
    flask_app_sa_name = pulumi_config["flask_app_sa_name"]
    flask_app_namespace = pulumi_config["flask_app_namespace"]

    with open('iam/flask_app_policy.json', 'r') as file:
        flask_app_policy_file = file.read()

    flask_app_policy = pulumi.Output.all(
        flask_app_table_name, flask_app_bucket_name).apply(
            lambda args: flask_app_policy_file
            .replace("{{TABLE_NAME}}", args[0])
            .replace("{{BUCKET_NAME}}", args[1])
    )

    flask_app_policy = aws.iam.Policy("flaskAppIAMPolicy",
        policy=flask_app_policy,
    )

    with open('iam/eks_oidc_role_trust_policy.json', 'r') as file:
        flask_app_role_trust_policy_file = file.read()

    flask_app_role_trust_policy = pulumi.Output.all(
        aws_account_id, oidc_provider_url).apply(
            lambda args: flask_app_role_trust_policy_file
            .replace("{{AWS_ACCOUNT_ID}}", args[0])
            .replace("{{OIDC_PROVIDER_URL}}", args[1])
            .replace("{{SA_NAME}}", flask_app_sa_name)
            .replace("{{NAMESPACE}}", flask_app_namespace)
    )

    flask_app_service_account_role = aws.iam.Role("flaskAppDefaultRole",
        assume_role_policy=flask_app_role_trust_policy,
    )

    flask_app_role_policy_attachment = aws.iam.RolePolicyAttachment("flaskAppRolePolicyAttachment",
        role=flask_app_service_account_role.name,
        policy_arn=flask_app_policy.arn,
    )

    flask_app_service_account = k8s.core.v1.ServiceAccount(flask_app_sa_name,
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=flask_app_sa_name,
            namespace=flask_app_namespace,
            annotations={
                "eks.amazonaws.com/role-arn": flask_app_service_account_role.arn
            }
        ),
        opts=pulumi.ResourceOptions(provider=context["eks"]["provider"])
    )


    pulumi.export("flask_app_service_account_name", flask_app_service_account.metadata.name)

    context["oidc_sa"] = {
        "flask_app": flask_app_service_account,
    }
