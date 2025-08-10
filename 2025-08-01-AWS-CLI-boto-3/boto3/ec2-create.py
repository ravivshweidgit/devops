import boto3

# Initialize the EC2 client
# Ensure your AWS credentials are configured (e.g., via AWS CLI or environment variables)
ec2_client = boto3.client('ec2') # Replace with your desired region

try:
    response = ec2_client.run_instances(
        ImageId='ami-0b00c1e12b92531a8',  # Replace with a valid AMI ID for your region
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro',
        KeyName='key-cli-01',  # Replace with an existing EC2 key pair name
        SecurityGroupIds=[
            'sg-0a4bbf87c1c16d60c',  # Replace with your security group ID
        ],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'MyBoto3Instance'
                    },
                ]
            },
        ]
    )

    for instance in response['Instances']:
        print(f"Launched EC2 Instance with ID: {instance['InstanceId']}")

except Exception as e:
    print(f"Error launching EC2 instance: {e}")