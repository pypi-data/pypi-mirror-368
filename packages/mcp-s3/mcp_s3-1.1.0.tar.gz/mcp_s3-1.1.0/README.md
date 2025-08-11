# MCP S3 File Manager

**S3 file operations for AI workflows** - Upload, download, and manage files in Amazon S3 through Model Context Protocol (MCP).

Perfect for AI assistants like Claude, Cursor, and any MCP-compatible client.

## ⚡ Quick Start

```bash
# Install and run (requires AWS credentials)
uvx mcp-s3 --root ~/uploads

# Or install globally
pip install mcp-s3
```

## 🔧 Setup

### 1. AWS Credentials
Create `.env` file in your project:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

### 2. Add to Your AI Tool

**Cursor IDE** - Add to `settings.json`:
```json
{
  "mcp": {
    "servers": {
      "s3": {
        "command": "uvx",
        "args": ["mcp-s3", "--root", "~/uploads"],
        "env": {
          "AWS_ACCESS_KEY_ID": "your_key",
          "AWS_SECRET_ACCESS_KEY": "your_secret", 
          "S3_BUCKET_NAME": "your-bucket"
        }
      }
    }
  }
}
```

**Claude Desktop** - Add to config:
```json
{
  "mcpServers": {
    "s3": {
      "command": "mcp-s3",
      "args": ["--root", "~/uploads"],
      "env": {
        "AWS_ACCESS_KEY_ID": "your_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret",
        "S3_BUCKET_NAME": "your-bucket"
      }
    }
  }
}
```

## 🛠️ What You Can Do

### Upload Files
```
@mcp Upload my config.json file to S3
@mcp Upload the backup.zip with 2-hour expiration
@mcp Upload report.pdf with force overwrite enabled
```
- **Preserves original filenames** (`config.json` → `config.json`)
- **Prevents accidental overwrites** (fails if file exists)
- **Force overwrite option** for intentional replacements
- **Progress tracking** for large files

### Download Files
```
@mcp Download config.json from S3 to ./downloads/
@mcp Download backup-2024.zip from S3
```

### List Files
```
@mcp List all files in S3
@mcp List files starting with "logs/"
@mcp Show me the first 50 files in the bucket
```

### Get File Info
```
@mcp Get info about config.json in S3
@mcp Show details for backup.zip
```

## 🚀 For Software Engineers

### Common Workflows

**1. Backup & Share Code**
```bash
# Upload project files
@mcp Upload my entire src/ directory to S3
@mcp Generate a 7-day URL for team-config.json
```

**2. CI/CD Integration**
```bash
# In your deployment scripts
mcp-s3 --root ./build upload dist.tar.gz
```

**3. Log Management**
```bash
# Upload application logs
@mcp Upload today's error.log to S3
@mcp List all log files from this month
```

**4. Asset Management**
```bash
# Manage project assets
@mcp Upload design-assets.zip
@mcp Download latest-assets.zip to ./assets/
```

### Development Setup
```bash
git clone https://github.com/dayongd1/mcp-s3.git
cd mcp-s3
uv sync
uv run mcp-s3 --root ~/test-uploads
```

### Testing
```bash
# Test basic functionality
python examples/test_mcp_server.py

# Test naming conflicts
python examples/test_naming_conflicts.py

# Test all features
python examples/test_download.py
python examples/test_list_files.py
python examples/test_get_file_info.py
```

## 🔒 Security Notes

- **Path Safety**: Prevents directory traversal attacks
- **Credential Management**: Uses environment variables (never hardcode keys)
- **Presigned URLs**: Time-limited access (default 24 hours)
- **Conflict Detection**: Prevents accidental file overwrites

## 📦 Installation Options

```bash
# Run without installing (recommended)
uvx mcp-s3

# Install globally
pip install mcp-s3

# Development install
git clone && uv sync
```

## 🚨 Troubleshooting

**"Bucket not found"**
```bash
# Check your bucket name and region
aws s3 ls s3://your-bucket-name
```

**"Access denied"**
```bash
# Verify AWS credentials
python examples/test_aws_connection.py
```

**"File already exists"**
```bash
# Use force overwrite or rename the file
@mcp Upload config.json with force overwrite enabled
```

## 📚 Links

- **PyPI**: https://pypi.org/project/mcp-s3/
- **GitHub**: https://github.com/dayongd1/mcp-s3
- **MCP Docs**: https://modelcontextprotocol.io/
- **AWS S3 Setup**: See `AWS_SETUP_GUIDE.md`

---

**Built with FastMCP** | **Python 3.10+** | **MIT License**