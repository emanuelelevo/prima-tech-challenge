import pulumi
import pulumi_aws as aws

def create_s3(context, pulumi_config):

    bucket_name = pulumi_config["bucket_name"]

    bucket = aws.s3.Bucket(bucket_name)

    ownership_controls = aws.s3.BucketOwnershipControls(
        "ownership-controls",
        bucket=bucket.id,
        rule=aws.s3.BucketOwnershipControlsRuleArgs(
            object_ownership="ObjectWriter",
        ),
    )

    public_access_block = aws.s3.BucketPublicAccessBlock(
        "public-access-block", bucket=bucket.id, block_public_acls=False
    )

    pulumi.export("bucket_name", bucket.id)
    
    context["bucket"] = bucket
