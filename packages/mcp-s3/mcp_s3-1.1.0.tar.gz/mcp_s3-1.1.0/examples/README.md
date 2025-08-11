# 🧪 Examples and Testing

This directory contains example scripts and testing utilities for the MCP S3 File Uploader.

## 📝 Files

### Testing Scripts
- **`test_aws_connection.py`** - Test your AWS credentials and S3 access
- **`test_mcp_server.py`** - Test basic MCP server functionality
- **`test_with_progress.py`** - Test upload progress tracking

### Setup Utilities
- **`setup_s3_bucket.py`** - Automated S3 bucket creation and configuration

## 🚀 Usage

### Test AWS Connection
```bash
# Make sure your .env file is configured first
python examples/test_aws_connection.py
```

### Test MCP Server
```bash
# Test basic upload functionality
python examples/test_mcp_server.py

# Test with progress tracking
python examples/test_with_progress.py
```

### Setup S3 Bucket
```bash
# Create and configure an S3 bucket
python examples/setup_s3_bucket.py
```

## 📋 Prerequisites

All examples require:
1. AWS credentials configured in `.env` file
2. Python dependencies installed: `pip install mcp-s3`
3. An upload directory (e.g., `~/mcp-uploads`)

## 🔧 Configuration

Create a `.env` file in the project root:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name_here
```
