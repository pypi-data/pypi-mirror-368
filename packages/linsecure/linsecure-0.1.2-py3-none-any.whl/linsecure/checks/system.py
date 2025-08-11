import platform
import subprocess

def check_os_info():
    results = ["[✓] System Info Check:"]

    # OS and kernel
    os_name = platform.system()
    os_release = platform.release()
    os_version = platform.version()
    results.append(f"[i] OS: {os_name} {os_release}")
    results.append(f"[i] Kernel Version: {os_version}")

    # Uptime
    try:
        uptime = subprocess.check_output(["uptime", "-p"]).decode().strip()
        results.append(f"[i] Uptime: {uptime}")
    except Exception as e:
        results.append(f"[i] Uptime check failed: {str(e)}")

    return "\n".join(results)
