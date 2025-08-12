import os
from dotenv import load_dotenv

load_dotenv()

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
ENVIRONMENT_TYPE = os.environ.get('ENVIRONMENT_TYPE', 'dev')
RELEASE_TYPE = os.environ.get('RELEASE_TYPE', 'stable')
OEM = "caiman"
