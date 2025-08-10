# MCP S3 File Uploader (mcp-s3)

A Model Context Protocol (MCP) server that provides secure file upload functionality to Amazon S3 with progress tracking and presigned URL generation.

## 🚀 Features

- **Secure S3 Upload**: Upload files to AWS S3 with automatic UUID-based naming
- **Progress Tracking**: Real-time upload progress for large files (>100MB uses multipart upload)
- **Presigned URLs**: Generate time-limited access URLs for uploaded files
- **Path Security**: Prevents directory traversal attacks with safe path joining
- **Environment Configuration**: Supports both CLI arguments and `.env` file configuration
- **FastMCP Integration**: Built with FastMCP framework for optimal MCP compatibility
- **Modern Python Support**: Full support for `uv` and `uvx` package managers
- **Multiple Execution Methods**: Run with traditional Python, uv, uvx, or direct script execution

## 📋 Prerequisites

- Python 3.10+
- AWS account with S3 access
- Valid AWS credentials (Access Key ID and Secret Access Key)
- An S3 bucket for file storage

## ⚡ Quick Start

### 1. Choose Your Installation Method

#### Method 1: Using uv (Recommended)
```bash
# Install dependencies and run
uv run python mcp_s3.py --root ~/mcp-uploads

# Or install the package and use the script
uv pip install -e .
uv run mcp-s3 --root ~/mcp-uploads
```

#### Method 2: Using uvx (Isolated Environment)
```bash
# Run directly from current directory
uvx --from . mcp-s3 --root ~/mcp-uploads

# Or if published to PyPI
uvx mcp-s3 --root ~/mcp-uploads
```

#### Method 3: Traditional Python
```bash
# With conda environment
conda activate your-env
python mcp_s3.py --root ~/mcp-uploads

# With pip/venv
pip install -r requirements.txt
python mcp_s3.py --root ~/mcp-uploads
```

#### Method 4: Direct Script Execution
```bash
# Make executable and run
chmod +x mcp_s3.py
./mcp_s3.py --root ~/mcp-uploads
```

### 2. Configure AWS Credentials
Create a `.env` file in the project root:
```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your_bucket_name_here
```

### 3. Test Your Setup
```bash
# Test AWS connection
python test_aws_connection.py

# Or with uv
uv run python test_aws_connection.py
```

### 4. Run the MCP Server
```bash
# Basic usage (recommended)
uv run python mcp_s3.py --root ~/mcp-uploads

# With custom bucket
uv run python mcp_s3.py --root ~/mcp-uploads --bucket my-custom-bucket

# Using uvx for isolation
uvx --from . mcp-s3 --root ~/mcp-uploads

# Traditional Python
python mcp_s3.py --root ~/mcp-uploads
```

## 🔧 MCP Integration

### Cursor IDE Setup

#### Using uv (Recommended)
Add this configuration to your `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "mcp-s3": {
      "command": "uv",
      "args": ["run", "python", "/path/to/mcp_s3.py", "--root", "/path/to/uploads"],
      "env": {
        "AWS_ACCESS_KEY_ID": "your_access_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret_key",
        "AWS_DEFAULT_REGION": "us-east-1",
        "S3_BUCKET_NAME": "your_bucket_name"
      }
    }
  }
}
```

#### Using uvx (Isolated Environment)
```json
{
  "mcpServers": {
    "mcp-s3": {
      "command": "uvx",
      "args": ["--from", "/path/to/project", "python", "mcp_s3.py", "--root", "/path/to/uploads"],
      "env": {
        "AWS_ACCESS_KEY_ID": "your_access_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret_key",
        "S3_BUCKET_NAME": "your_bucket_name"
      }
    }
  }
}
```

#### Traditional Python
```json
{
  "mcpServers": {
    "mcp-s3": {
      "transport": "stdio",
      "command": "/path/to/python",
      "args": [
        "/path/to/mcp_s3.py",
        "--root",
        "/path/to/upload/directory"
      ],
      "env": {
        "AWS_ACCESS_KEY_ID": "your_access_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret_key",
        "AWS_DEFAULT_REGION": "us-east-1",
        "S3_BUCKET_NAME": "your_bucket_name"
      }
    }
  }
}
```

### Claude Desktop Setup
Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "s3-uploader": {
      "command": "python",
      "args": [
        "/path/to/mcp_s3.py",
        "--bucket", "your-bucket-name",
        "--root", "/path/to/uploads"
      ]
    }
  }
}
```

## 🛠️ Available Tools

### `upload_file`
Upload a local file to S3 and return a presigned URL.

**Parameters:**
- `local_path` (string, required): Path to the file relative to the configured root directory
- `expires_in` (integer, optional): URL expiration time in seconds (default: 86400 = 24 hours)

**Returns:**
- `url`: Presigned URL for accessing the uploaded file
- `size`: File size in bytes
- `mime_type`: Detected MIME type of the file
- `s3_key`: Generated S3 object key (UUID + file extension)

**Example Usage in MCP Client:**
```
@mcp-s3 upload the document.pdf file with 2-hour expiration
```

## 📁 File Structure

```
mcp-s3/
├── mcp_s3.py                   # Main MCP server
├── pyproject.toml              # Modern Python project configuration
├── requirements.txt            # Python dependencies (legacy)
├── __main__.py                 # Module entry point
├── test_aws_connection.py      # AWS credentials tester
├── test_mcp_server.py          # MCP server functionality test
├── test_with_progress.py       # Progress tracking test
├── test_execution_methods.py   # Test all execution methods
├── generate_mcp_config.py      # Generate Cursor MCP config
├── setup_s3_bucket.py          # S3 bucket setup script
├── .env                        # AWS credentials (create from env_example.txt)
├── env_example.txt             # Environment variables template
├── USAGE.md                    # Detailed usage guide
├── AWS_SETUP_GUIDE.md          # AWS setup instructions
└── README.md                   # This file
```

## 🔒 Security Features

- **Path Traversal Protection**: Prevents access to files outside the configured root directory
- **Presigned URLs**: Time-limited access to uploaded files without exposing AWS credentials
- **Environment Variables**: Sensitive credentials stored in `.env` file (not committed to git)
- **UUID File Naming**: Prevents filename collisions and adds obscurity

## 📊 Progress Tracking

- **Small Files** (<100MB): Progress reported at key milestones (0%, 25%, 90%, 100%)
- **Large Files** (≥100MB): Multipart upload with detailed progress per chunk
- **Real-time Updates**: MCP clients receive progress notifications during upload

## 🧪 Testing

### Test AWS Connection
```bash
# Traditional Python
python test_aws_connection.py

# With uv
uv run python test_aws_connection.py
```

### Test MCP Server
```bash
# Traditional Python
python test_mcp_server.py

# With uv
uv run python test_mcp_server.py
```

### Test with Progress Tracking
```bash
# Traditional Python
python test_with_progress.py

# With uv
uv run python test_with_progress.py
```

### Test All Execution Methods
```bash
# Verify all installation methods work
python test_execution_methods.py
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   # With uv
   uv sync  # Install all dependencies
   
   # Traditional pip
   pip install -r requirements.txt
   ```

2. **"Missing required environment variables"**
   - Ensure your `.env` file exists and contains all required AWS credentials
   - Check your `.env` file format matches the example

3. **AWS Credentials Not Found**
   - Check your `.env` file
   - Verify AWS CLI configuration: `aws configure list`
   - Ensure environment variables are properly loaded

4. **"File not found"**
   - Check that the file exists in the configured root directory
   - Verify the file path is relative to the root directory

5. **"Access denied to bucket"**
   - Verify your AWS credentials have S3 permissions
   - Ensure the bucket name is correct and exists
   - Check S3 bucket policies and IAM permissions

6. **"Path escapes allowed root"**
   - File path must be within the configured root directory
   - Use relative paths only (no `../` traversal)

7. **Permission Denied**
   - Ensure the upload directory exists and is writable
   - Check file system permissions

8. **Port Already in Use**
   - The server uses stdio transport, no port conflicts should occur
   - If using a different transport, check for port conflicts

## 📝 Configuration Options

### CLI Arguments
- `--bucket`: S3 bucket name (overrides environment variable)
- `--root`: Root directory for file uploads (required)

### Environment Variables
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key  
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)
- `S3_BUCKET_NAME`: Target S3 bucket name

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python test_mcp_server.py`
5. Submit a pull request

## 📄 License

This project is open source. Please ensure you comply with AWS terms of service when using S3.

## 📚 Additional Resources

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp) | [Documentation](https://gofastmcp.com)
- [UV Package Manager](https://github.com/astral-sh/uv) - Fast Python package installer
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Cursor IDE](https://cursor.sh/)
- [Detailed Usage Guide](./USAGE.md)
- [AWS Setup Guide](./AWS_SETUP_GUIDE.md)

---

Built with ❤️ using FastMCP for seamless LLM integration
