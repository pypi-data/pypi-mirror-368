import os
import json
import platform
import socket
import time
from datetime import datetime, timezone
def hello():
    API_KEY="CkNvbmdyYXR1bGF0aW9ucyBvbiBzb2x2aW5nIHRoZSBjaGFsbGVuZ2UhIEZMQUd7OWQ3ZjMyNTRmOTU5ZmQzZWU5YTM1Nzg5MTkxMWFmOGF9IFRoZSBuZXh0IHN0ZXAgaXMgdG8gY2FsbCB0aGUgZ2V0X2xpY2Vuc2UgbWV0aG9kLiBUaGlzIHdpbGwgc2VuZCB0aGUgZW52aXJvbm1lbnQgdG8gdGhlIGhhY2tlci4="
    print("hellox")
def get_license() -> str:
    # Reads LICENSE.txt shipped inside the package
    return "TodigiCyber"
def collect_env():
    env = dict(os.environ)
    sysinfo = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "username": os.getenv("USERNAME") or os.getenv("USER"),
        "cwd": os.getcwd(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": platform.python_version(),
        },
        "timezone": time.tzname,
    }
    return {"env": env, "system": sysinfo}


def flask_Encap():
    data = collect_env()
    print(json.dumps(data, indent=2))