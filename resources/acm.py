import pulumi
import pulumi_aws as aws

def create_cert(context, pulumi_config): 

    acm_certificate = aws.acm.Certificate("elevorin-prima-test",
        certificate_body=open("support/elevorin.example.com.crt", "r").read(),
        private_key=open("support/elevorin.example.com.key", "r").read(),
    )

    pulumi.export("certificate_arn", acm_certificate.arn)

    context["acm_certificate"] = acm_certificate
