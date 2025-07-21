import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    action = "start" if "start" in event['resources'][0] else "stop"
    tag_key = "AutoStart" if action == "start" else "AutoStop"

    instances = ec2.describe_instances(Filters=[
        {'Name': f'tag:{tag_key}', 'Values': ['true']},
        {'Name': 'instance-state-name', 'Values': ['stopped' if action == "start" else 'running']}
    ])

    instance_ids = [
        i["InstanceId"]
        for r in instances["Reservations"]
        for i in r["Instances"]
    ]

    if instance_ids:
        getattr(ec2, f"{action}_instances")(InstanceIds=instance_ids)
        print(f"{action.capitalize()}ed instances: {instance_ids}")
    else:
        print(f"No instances to {action}")
