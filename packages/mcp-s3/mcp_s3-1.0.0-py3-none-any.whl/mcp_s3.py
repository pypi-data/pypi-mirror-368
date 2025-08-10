#!/usr/bin/env python3
"""
MCP S3 File Uploader - A Model Context Protocol server for S3 uploads
Usage:
  python mcp_s3.py --bucket mybucket --root ~/Uploads
"""
import argparse
import mimetypes
import os
import uuid
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from fastmcp import FastMCP, Context
from pydantic import BaseModel
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Parse CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("--bucket", help="Target S3 bucket name (overrides .env)")
parser.add_argument("--root", required=True, help="Absolute path on disk allowed for uploads")
args = parser.parse_args()

ROOT = os.path.abspath(os.path.expanduser(args.root))

# Get bucket name from CLI args or environment
BUCKET = args.bucket or os.getenv("S3_BUCKET_NAME")
if not BUCKET:
    raise ValueError("S3 bucket name must be provided via --bucket argument or S3_BUCKET_NAME in .env file")

# Initialize S3 client with credentials from environment
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

if aws_access_key and aws_secret_key:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )
else:
    # Fall back to default credential chain (AWS CLI, IAM roles, etc.)
    s3 = boto3.client("s3")

# Initialize FastMCP
mcp = FastMCP("MCP S3 File Uploader")


class UploadResponse(BaseModel):
    url: str
    size: int
    mime_type: str
    s3_key: str


def safe_join(root: str, user_path: str) -> str:
    """Safely join paths and prevent directory traversal"""
    abs_path = os.path.abspath(os.path.join(root, user_path))
    if not abs_path.startswith(root):
        raise ValueError("Path escapes allowed root")
    return abs_path


def generate_presigned_url(key: str, expires_in: int) -> str:
    """Generate a presigned URL for the uploaded file"""
    try:
        return s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=expires_in,
        )
    except ClientError as e:
        raise ValueError(f"Failed generating presigned URL: {e}")


async def upload_with_progress(local_path: str, bucket: str, key: str, ctx: Context):
    """Upload file with progress reporting using multipart upload for better control"""
    file_size = os.path.getsize(local_path)
    
    # Report start
    await ctx.report_progress(progress=0, total=100)
    
    try:
        # For files larger than 100MB, use multipart upload with progress
        if file_size > 100 * 1024 * 1024:  # 100MB
            # Initialize multipart upload
            response = s3.create_multipart_upload(Bucket=bucket, Key=key)
            upload_id = response['UploadId']
            
            parts = []
            part_size = 50 * 1024 * 1024  # 50MB parts
            part_number = 1
            
            with open(local_path, 'rb') as f:
                while True:
                    data = f.read(part_size)
                    if not data:
                        break
                    
                    # Upload part
                    part_response = s3.upload_part(
                        Bucket=bucket,
                        Key=key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=data
                    )
                    
                    parts.append({
                        'ETag': part_response['ETag'],
                        'PartNumber': part_number
                    })
                    
                    # Report progress
                    progress = (part_number * part_size * 100) // file_size
                    progress = min(progress, 95)  # Cap at 95% until completion
                    await ctx.report_progress(progress=progress, total=100)
                    
                    part_number += 1
            
            # Complete multipart upload
            s3.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
        else:
            # For smaller files, use simple upload with progress checkpoints
            await ctx.report_progress(progress=25, total=100)
            s3.upload_file(local_path, bucket, key)
            await ctx.report_progress(progress=90, total=100)
    
    except ClientError as e:
        await ctx.report_progress(progress=0, total=100)  # Reset on error
        raise
    
    # Report completion
    await ctx.report_progress(progress=100, total=100)


@mcp.tool()
async def upload_file(local_path: str, ctx: Context, expires_in: int = 86400) -> UploadResponse:
    """Upload a local file to S3 and return a presigned URL with progress tracking"""
    
    # Log the upload start
    await ctx.info(f"Starting upload of {local_path}")
    
    # Validate and resolve the local path
    full_local_path = safe_join(ROOT, local_path)
    if not os.path.isfile(full_local_path):
        raise ValueError("File not found")
    
    # Get file info
    file_size = os.path.getsize(full_local_path)
    ext = os.path.splitext(full_local_path)[1]
    s3_key = f"{uuid.uuid4().hex}{ext}"
    
    await ctx.info(f"File size: {file_size:,} bytes, uploading as {s3_key}")
    
    # Upload to S3 with progress tracking
    try:
        await upload_with_progress(full_local_path, BUCKET, s3_key, ctx)
    except ClientError as e:
        await ctx.error(f"Failed to upload file: {e}")
        raise ValueError(f"Failed to upload file: {e}")
    
    # Generate presigned URL
    presigned_url = generate_presigned_url(s3_key, expires_in)
    
    # Determine MIME type
    mime_type = mimetypes.guess_type(full_local_path)[0] or "application/octet-stream"
    
    await ctx.info(f"Upload completed successfully. Presigned URL expires in {expires_in} seconds.")
    
    return UploadResponse(
        url=presigned_url,
        size=file_size,
        mime_type=mime_type,
        s3_key=s3_key
    )


def main():
    """Main entry point for the MCP S3 server"""
    mcp.run()


if __name__ == "__main__":
    main()