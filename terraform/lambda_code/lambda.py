import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Determine action from event
    resource_str = event['resources'][0]
    action: str = "start" if "start" in resource_str else "stop"
    tag_key: str = "AutoStart" if action == "start" else "AutoStop"
    target_state: str = "stopped" if action == "start" else "running"

    try:
        response = ec2.describe_instances(Filters=[
            {'Name': f'tag:{tag_key}', 'Values': ['true']},
            {'Name': 'instance-state-name', 'Values': [target_state]}
        ])
    except Exception as e:
        print("Error while describing instances:", str(e))
        raise

    instance_ids: list[str] = [
        i["InstanceId"]
        for r in response.get("Reservations", [])
        for i in r.get("Instances", [])
    ]

    if instance_ids:
        try:
            ec2_action = getattr(ec2, f"{action}_instances")
            result = ec2_action(InstanceIds=instance_ids)
        except Exception as e:
            print(f"Error during {action} operation:", str(e))
            raise
    else:
        print(f"No instances to {action}")
