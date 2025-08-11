# AWS Setup Guide - Getting Your Credentials

This guide will help you get the AWS credentials needed to configure your `aws.cfg` file.

## 🔑 What You Need

You need to create an AWS Access Key ID and Secret Access Key for programmatic access to AWS services.

## 📋 Prerequisites

1. **AWS Account**: You must have an active AWS account
2. **Admin Access**: You need permissions to create IAM users and policies

## 🚀 Step-by-Step Instructions

### Step 1: Sign in to AWS Console

1. Go to [AWS Management Console](https://console.aws.amazon.com/)
2. Sign in with your AWS account credentials
3. Make sure you're in the correct AWS region (you can change it in the top-right corner)

### Step 2: Navigate to IAM Service

1. In the AWS Console search bar, type "IAM" and click on it
2. Or go directly to: https://console.aws.amazon.com/iam/

### Step 3: Create an IAM User

1. In the IAM dashboard, click **"Users"** in the left sidebar
2. Click **"Create user"**
3. Enter a user name (e.g., `boto3-lab-user`)
4. **Important**: Check the box **"Provide user access to the AWS Management Console"**
5. **Choose Option 2**: Select **"I want to create an IAM user"** (not Identity Center)
6. Click **"Next"**

### Step 4: Set Permissions

1. Choose **"Attach policies directly"**
2. Search for and select: **`AdministratorAccess`**
   - This gives full access to all AWS services (recommended for learning/development)
   - Covers all scenarios: VPC, EC2, IAM, SSM, and more
3. Click **"Next"**
4. Review the permissions and click **"Create user"**

### Step 5: Create Access Keys

1. Click on your newly created user
2. Go to the **"Security credentials"** tab
3. Click **"Create access key"**
4. Choose **"Command Line Interface (CLI)"**
5. Check the confirmation box
6. Click **"Next"**
7. Add a description: **"boto3 VPC Lab - Programmatic access for AWS automation"** and click **"Create access key"**

### Step 6: Save Your Credentials

**⚠️ IMPORTANT**: This is the only time you'll see the Secret Access Key!

1. **Download the .csv file** or copy the credentials
2. You'll see:
   - **Access key ID**: Something like `AKIAIOSFODNN7EXAMPLE`
   - **Secret access key**: Something like `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
3. **Save these credentials** - you'll need them for your `aws.cfg` file in the next step

### Step 7: Update Your aws.cfg File

Now update your `aws.cfg` file with the real credentials:

1. **Open the aws.cfg file** in your project directory:
   ```bash
   nano aws.cfg
   ```

2. **Replace the placeholder values** with your real credentials:
   ```ini
   [AWS]
   # Your AWS Access Key ID
   access_key_id = YOUR_REAL_ACCESS_KEY_ID_HERE
   
   # Your AWS Secret Access Key  
   secret_access_key = YOUR_REAL_SECRET_ACCESS_KEY_HERE
   
   # Default AWS region
   region = us-east-1
   
   # Default output format
   output_format = json
   ```

3. **Save the file** (Ctrl+X, then Y, then Enter in nano)

### Step 8: Choose Your AWS Region

Common AWS regions:
- **us-east-1** (N. Virginia) - Most popular
- **us-west-2** (Oregon)
- **eu-west-1** (Ireland)
- **ap-southeast-1** (Singapore)

## 📝 Configure Your aws.cfg File

Now update your `aws.cfg` file with the credentials you just created:

```bash
# Edit the aws.cfg file
nano aws.cfg
```

Replace the placeholder values:

```ini
[AWS]
# Your AWS Access Key ID
access_key_id = AKIAIOSFODNN7EXAMPLE

# Your AWS Secret Access Key  
secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Default AWS region
region = us-east-1

# Default output format
output_format = json
```

## 🔒 Security Best Practices

1. **Never commit credentials to Git**: Add `aws.cfg` to your `.gitignore` file
2. **Use IAM roles when possible**: For production environments
3. **Rotate keys regularly**: Change your access keys every 90 days
4. **Limit permissions**: Only grant the minimum required permissions

## 🧪 Test Your Configuration

After updating `aws.cfg`, test your setup:

```bash
# Check if everything is configured correctly
./setup.sh --check-only

# If all checks pass, run the full setup
./setup.sh
```

## 🆘 Troubleshooting

### "Access Denied" Errors
- Check if your IAM user has the required permissions
- Verify your Access Key ID and Secret Access Key are correct
- Ensure you're using the correct AWS region

### "Invalid credentials" Errors
- Double-check your Access Key ID and Secret Access Key
- Make sure there are no extra spaces in your aws.cfg file
- Verify the credentials are active in your AWS account

### "Region not found" Errors
- Use a valid AWS region code (e.g., us-east-1, not "US East")
- Check the AWS region list for valid options

## 📚 Additional Resources

- [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [AWS Regions and Endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html)

## 🎯 Next Steps

Once your `aws.cfg` is properly configured:

1. Run `./setup.sh --check-only` to verify everything
2. Run `./setup.sh` to complete the setup
3. Follow the README.md for using the VPC automation

---

**Happy Learning! 🚀**
