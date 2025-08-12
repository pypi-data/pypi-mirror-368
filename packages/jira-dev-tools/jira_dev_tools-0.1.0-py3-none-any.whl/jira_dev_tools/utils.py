import re
import subprocess
from typing import Optional

def setup_credentials():
    subprocess.call('./setup_credentials.sh', shell=True)

def extract_key_from_input(text: str) -> Optional[str]:
	"""Extract a Jira ticket key from text"""
	match = re.match(r"^([A-Za-z]{2,4}-\d{,8})", text)
	return match.group(1).upper() if match else None
