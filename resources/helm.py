import pulumi
import pulumi_kubernetes as k8s

def create_helm(context, pulumi_config):

    aws_region = pulumi_config["aws_region"]

    helm_app_values = {
        "serviceAccount": {
            "enabled": True
        },
        "env": {
            "AWS_REGION": aws_region,
            "S3_BUCKET": context["bucket"].id,
            "DYNAMODB_TABLE": context["table"].name,
        }
    }

    if context["eks"] == "localdev":
        localstack_url = pulumi_config["localstack_url"]
        # Set provider back to KUBECONFIG environment variable
        # and replace references for missing resources
        context["eks"] = {
            "provider": k8s.Provider("provider"),
            "helm_lb_controller": context["bucket"],
        }
        context["oidc_sa"] = {
            "flask_app": context["bucket"],
        }
        helm_app_values["serviceAccount"]["enabled"] = False
        helm_app_values["env"]["AWS_ACCESS_KEY_ID"] = "test"
        helm_app_values["env"]["AWS_SECRET_ACCESS_KEY"] = "test"
        helm_app_values["env"]["AWS_ENDPOINT_URL"] = localstack_url
    
    helm_app_deps = [
        context["eks"]["helm_lb_controller"],
        context["bucket"],
        context["table"],
        context["oidc_sa"]["flask_app"],
    ]

    helm_app = k8s.helm.v3.Release("elevorin-prima-test",
        k8s.helm.v3.ReleaseArgs(
            name="elevorin-prima-test",
            chart="charts/flask-app",
            namespace="default",
            values=helm_app_values
        ),
        opts=pulumi.ResourceOptions(
            provider=context["eks"]["provider"],
            depends_on=helm_app_deps
        )
    )

    context["helm_app"] = helm_app
