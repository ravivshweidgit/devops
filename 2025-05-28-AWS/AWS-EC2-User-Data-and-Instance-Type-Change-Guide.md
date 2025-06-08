# AWS EC2 User Data and Instance Type Change Guide

This guide demonstrates how to use EC2 User Data to automatically install software during instance launch and how to change instance types.

## Part 1: Using User Data to Install Docker

### Step 1: Create EC2 Instance with User Data

Follow the standard EC2 creation process as described in the getting started guide, but with one important addition in the **Advanced details** section.

### Step 2: Configure User Data Script

1. In the **Advanced details** section, scroll down to find **User data**

2. Enter the following script:
   ```bash
   #!/bin/bash
   sudo yum update -y
   sudo yum install -y docker
   ```

3. **Launch instance** as normal

### Step 3: Connect to Your Instance

1. Navigate to the Instances page:
   ```
   https://eu-north-1.console.aws.amazon.com/ec2/home?region=eu-north-1#Instances:
   ```

2. **Click the refresh button** (AWS console doesn't auto-refresh efficiently)

3. Select the instance line and click **Connect**

4. Copy the SSH connection command from the **SSH client** tab

### Step 4: Test the User Data Installation

1. Navigate to your local directory containing the AWS key file

2. Connect using the copied SSH command:
   ```bash
   ssh -i "key01.pem" ec2-user@ec2-51-20-52-29.eu-north-1.compute.amazonaws.com
   ```

3. Example connection session:
   ```bash
   ravivm@ravivm-N501VW:~/Downloads$ ssh -i "key01.pem" ec2-user@ec2-51-20-52-29.eu-north-1.compute.amazonaws.com
   
      ,     #_
      ~\_  ####_        Amazon Linux 2023
     ~~  \_#####\
     ~~     \###|
     ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
      ~~       V~' '->
       ~~~         /
         ~~._.   _/
            */ */
          _/m/'
   
   Last login: Wed May 28 18:26:46 2025 from 79.177.133.211
   ```

4. Verify Docker installation:
   ```bash
   [ec2-user@ip-172-31-27-102 ~]$ docker --version
   Docker version 25.0.8, build 0bab007
   ```

**Success!** Docker is installed and configured via User Data - goal achieved for this phase.

## Part 2: Change Instance Type

### Step 1: Stop the Instance

1. Go to the Instances page
2. Select your instance
3. **Instance State** → **Stop instance**
4. Wait for the instance to fully stop

### Step 2: Change Instance Type

1. With the stopped instance selected, go to **Actions** → **Instance settings** → **Change instance type**

2. Select **t3.nano** from the dropdown

3. Click **Change**

### Step 3: Start and Reconnect

1. **Start the instance** (Instance State → Start instance)

2. Once running, go to **Connect** → **SSH client** tab

3. **Copy the new connection command** (the public DNS will have changed)

4. Connect using the updated command:
   ```bash
   ssh -i "key01.pem" ec2-user@ec2-16-170-237-87.eu-north-1.compute.amazonaws.com
   ```

## Key Points About User Data

- **Runs once**: User Data scripts execute only during the first boot of an instance
- **Root privileges**: Scripts run with root privileges by default
- **Logging**: Check `/var/log/cloud-init-output.log` for User Data script execution logs
- **Format**: Must start with `#!/bin/bash` or appropriate shebang for the script type

## Key Points About Instance Type Changes

- **Stop required**: You must stop the instance before changing types
- **New public IP**: The instance will get a new public IP/DNS after restart
- **Data persistence**: EBS root volumes retain data through instance type changes
- **Compatibility**: Ensure the new instance type supports your workload requirements

## Troubleshooting

### User Data Issues
- If software isn't installed, check `/var/log/cloud-init-output.log`
- Ensure proper syntax in the User Data script
- Remember that User Data only runs on first boot

### Instance Type Change Issues
- If change option is grayed out, ensure instance is fully stopped
- Some instance types may not be available in all regions
- Check that your account has permission to use the target instance type

## Clean Up

Remember to terminate your instance and check for any remaining volumes when you're done testing to avoid unnecessary charges.