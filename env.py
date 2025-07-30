import os

REVOKE_URL=os.environ.get("REVOKE_URL","")
REDIRECT_URI=os.environ.get("REDIRECT_URI","")
CLIENT_ID=os.environ.get("CLIENT_ID","")
CLIENT_SECRET=os.environ.get("CLIENT_SECRET","")
ENV=os.environ.get("ENV", "prod")

GOOGLE_PROJECT_ID=os.environ.get("GOOGLE_PROJECT_ID", "")
GOOGLE_LOCATION=os.environ.get("GOOGLE_LOCATION", "")
GOOGLE_LLM_MODEL=os.environ.get("GOOGLE_LLM_MODEL", "")
GOOGLE_BUCKET_NAME=os.environ.get("GOOGLE_BUCKET_NAME", "")

RESOURCES_DIR = os.environ.get("RESOURCES_DIR", "resources")
