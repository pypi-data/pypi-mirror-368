import time
import json
import uuid
import boto3
import io
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse


class APILoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, bucket, region, key_prefix="logs/"):
        super().__init__(app)
        self.bucket = bucket
        self.region = region
        self.key_prefix = key_prefix
        self.s3 = boto3.client("s3", region_name=region)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # --- Capture request body and files ---
        request_body = await request.body()
        request_files = {}
        if "multipart/form-data" in request.headers.get("content-type", ""):
            form = await request.form()
            for key, value in form.items():
                if hasattr(value, "filename") and value.filename:
                    file_content = await value.read()
                    request_files[value.filename] = file_content

        # --- Call the next middleware / route handler ---
        response = await call_next(request)

        # --- Capture response body and files ---
        response_body = b""
        if isinstance(response, StreamingResponse):
            # Consume streaming response into bytes (might be memory-heavy)
            async for chunk in response.body_iterator:
                response_body += chunk
            response.body_iterator = iter([response_body])

        duration = time.time() - start_time

        # --- Upload request.json ---
        request_data = {
            "id": request_id,
            "timestamp": time.time(),
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": request_body.decode("utf-8", errors="ignore"),
        }
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"{self.key_prefix}{request_id}/request.json",
            Body=json.dumps(request_data, indent=2).encode("utf-8"),
            ContentType="application/json",
        )

        # --- Upload request_files ---
        for filename, file_content in request_files.items():
            self.s3.put_object(
                Bucket=self.bucket,
                Key=f"{self.key_prefix}{request_id}/request_files/{filename}",
                Body=file_content,
            )

        # --- Upload response.json ---
        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "duration": duration,
        }
        if response_body:
            try:
                response_data["body"] = response_body.decode("utf-8", errors="ignore")
            except Exception:
                response_data["body"] = "<binary data>"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"{self.key_prefix}{request_id}/response.json",
            Body=json.dumps(response_data, indent=2).encode("utf-8"),
            ContentType="application/json",
        )

        # --- Upload response_files if applicable ---
        if "application/octet-stream" in response.headers.get("content-type", ""):
            self.s3.put_object(
                Bucket=self.bucket,
                Key=f"{self.key_prefix}{request_id}/response_files/output.bin",
                Body=response_body,
            )

        return response
