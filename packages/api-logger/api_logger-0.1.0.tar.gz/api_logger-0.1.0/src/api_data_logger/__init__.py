from .utils import APILoggerMiddleware

def use_api_logger(app, bucket, region, key_prefix="logs/"):
    app.add_middleware(APILoggerMiddleware, bucket=bucket, region=region, key_prefix=key_prefix)
