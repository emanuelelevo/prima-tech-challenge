import pulumi
import pulumi_aws as aws

def create_table(context, pulumi_config): 

    table_name = pulumi_config["table_name"]

    table = aws.dynamodb.Table(table_name,
        billing_mode="PAY_PER_REQUEST",
        hash_key="email",
        attributes=[{
            "name": "email",
            "type": "S",
        }],
    )

    pulumi.export("table_name", table.name)

    context["table"] = table
