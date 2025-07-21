# routers/upload.py
from fastapi import APIRouter, HTTPException
from core.config import settings
from botocore.client import Config
import boto3

router = APIRouter(prefix="/upload", tags=["upload"])

# Cliente S3/Filebase
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.FILEBASE_KEY,
    aws_secret_access_key=settings.FILEBASE_SECRET,
    endpoint_url="https://s3.filebase.com",
    region_name="us-east-1",
    config=Config(signature_version="s3v4")
)

@router.get("/presigned-url")
def get_presigned_url(filename: str):
    key = f"products/{filename}"
    try:
        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.FILEBASE_BUCKET,
                "Key": key,
                "ContentType": "image/webp"
            },
            ExpiresIn=3600
        )
    except Exception as e:
        raise HTTPException(500, f"Error generando URL: {e}")
    return {"url": url, "key": key}
