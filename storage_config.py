"""
Storage backend configuration, shared by agent_core.py (agent memory) and
session_index.py (dashboard/chat display history).

Controlled entirely by environment variables so you can flip between
local dev and S3 without touching code:

    SESSION_BACKEND       "local" (default) or "s3"
    S3_SESSION_BUCKET     required if SESSION_BACKEND=s3
    S3_SESSION_PREFIX     optional key prefix inside the bucket
                          (default: "returns-agent/")
    AWS_REGION            optional -- normally picked up from your
                          AWS profile/config already

The boto3 S3 client is created lazily, and only if SESSION_BACKEND=s3,
so nothing here requires boto3/AWS credentials to be present for local
runs.

IAM permissions needed on the bucket for the app's IAM user/role:
    s3:GetObject, s3:PutObject, s3:ListBucket
(s3:DeleteObject too, if you later add a "delete session" feature.)
"""

import os

SESSION_BACKEND = os.environ.get("SESSION_BACKEND", "local").strip().lower()
S3_BUCKET = os.environ.get("S3_SESSION_BUCKET", "").strip()
S3_PREFIX = os.environ.get("S3_SESSION_PREFIX", "returns-agent/").strip("/")
if S3_PREFIX:
    S3_PREFIX += "/"
AWS_REGION = os.environ.get("AWS_REGION") or None

if SESSION_BACKEND not in ("local", "s3"):
    raise RuntimeError(
        f"Invalid SESSION_BACKEND={SESSION_BACKEND!r} -- must be 'local' or 's3'."
    )


def require_s3_bucket() -> None:
    """Raise a clear error early if S3 mode is on but misconfigured."""
    if SESSION_BACKEND == "s3" and not S3_BUCKET:
        raise RuntimeError(
            "SESSION_BACKEND=s3 but S3_SESSION_BUCKET is not set. "
            "Set S3_SESSION_BUCKET to the name of the bucket you want "
            "session data written to."
        )


_s3_client = None


def get_s3_client():
    """Lazily create (and cache) the boto3 S3 client. Only called when
    SESSION_BACKEND=s3, so boto3 doesn't need to be installed/configured
    for local-only usage."""
    global _s3_client
    if _s3_client is None:
        import boto3
        _s3_client = boto3.client("s3", region_name=AWS_REGION) if AWS_REGION else boto3.client("s3")
    return _s3_client


def using_s3() -> bool:
    return SESSION_BACKEND == "s3"