# 🚀 AWS Setup Guide for MCP S3 Upload Server

## Step 1: Get AWS Credentials

### Method A: AWS Console (Recommended for new accounts)

1. **Log into AWS Console**: Go to [aws.amazon.com](https://aws.amazon.com) and sign in
2. **Create IAM User**:
   - Go to **IAM** service → **Users** → **Create user**
   - Username: `mcp-server-user`
   - Select: **Programmatic access**
3. **Set Permissions**:
   - Click **Attach policies directly**
   - Search and select: `AmazonS3FullAccess`
   - (For production, use more restrictive permissions)
4. **Save Credentials**:
   - Download the CSV file with your credentials
   - **Important**: Save these keys securely - you won't see the secret key again!

### Method B: AWS CLI Configuration

```bash
# Install AWS CLI
pip install awscli

# Configure with your credentials
aws configure
# Enter when prompted:
#   AWS Access Key ID: [Your access key]
#   AWS Secret Access Key: [Your secret key] 
#   Default region: us-east-1 (or your preferred region)
#   Default output format: json
```

## Step 2: Run the Setup Script

```bash
# Make sure boto3 is installed
pip install boto3

# Run the automated setup
python setup_s3_bucket.py
```

This script will:
- ✅ Verify your AWS credentials
- ✅ Create a uniquely named S3 bucket
- ✅ Configure security settings (block public access)
- ✅ Enable encryption and versioning
- ✅ Set up automatic cleanup (30-day retention)
- ✅ Test all permissions

## Step 3: Test Your Setup

The script will output a command like:
```bash
python mcp_box.py --bucket mcp-uploads-abc12345 --root /path/to/uploads
```

**Save this bucket name!** You'll need it to run your MCP server.

## Step 4: Create Upload Directory

```bash
# Create a directory for files to upload
mkdir -p ~/mcp-uploads
echo "Hello MCP!" > ~/mcp-uploads/test.txt
```

## Step 5: Start Your MCP Server

```bash
# Replace with your actual bucket name from Step 2
python mcp_box.py --bucket mcp-uploads-abc12345 --root ~/mcp-uploads
```

## Step 6: Test the Server

```bash
# Update test script with your bucket name
sed -i 's/your-bucket-name/mcp-uploads-abc12345/g' test_mcp_server.py

# Run the test
python test_mcp_server.py
```

---

## 🔒 Security Best Practices

### Production IAM Policy (More Restrictive)

Instead of `AmazonS3FullAccess`, create a custom policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject", 
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::mcp-uploads-*/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::mcp-uploads-*"
        }
    ]
}
```

### Environment Variables (Alternative to AWS CLI)

```bash
# Add to your ~/.bashrc or ~/.zshrc
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-east-1"
```

---

## 🆘 Troubleshooting

### "AccessDenied" Errors
- Check your IAM user has S3 permissions
- Verify AWS credentials are correctly configured

### "BucketAlreadyExists" 
- The script will automatically retry with a new name
- S3 bucket names must be globally unique

### "RegionMismatch"
- Ensure your AWS CLI region matches where you want the bucket

### Test AWS Connection
```python
import boto3
try:
    s3 = boto3.client('s3')
    print("✅ AWS connection successful")
    print("Buckets:", [b['Name'] for b in s3.list_buckets()['Buckets']])
except Exception as e:
    print(f"❌ AWS connection failed: {e}")
```

---

## 💰 Cost Considerations

For a new AWS account:
- **S3 Storage**: ~$0.023/GB/month
- **Requests**: ~$0.0004 per 1000 PUT requests  
- **Data Transfer**: First 1GB/month free

**Example**: 1000 file uploads (1MB each) ≈ $0.05/month

---

## Next Steps

Once setup is complete, you can:
1. Integrate with Claude Desktop
2. Add authentication
3. Implement file type restrictions
4. Set up monitoring and logging 