import subprocess
import pwd
import grp
import os

EXCLUDED_DIRS = ["/proc", "/sys", "/dev", "/run", "/mnt", "/media", "/snap"]

def get_owner(path):
    try:
        stat = os.stat(path)
        user = pwd.getpwuid(stat.st_uid).pw_name
        group = grp.getgrgid(stat.st_gid).gr_name
        return f"{user}:{group}"
    except Exception:
        return "unknown"

def run_find(path, type_flag):
    try:
        cmd = f"find {path} -xdev -type {type_flag} -perm -0002 2>/dev/null"
        return subprocess.check_output(cmd, shell=True).decode().strip().splitlines()
    except subprocess.CalledProcessError:
        return []

def check_file_permissions():
    results = ["[✓] Permissions Check:"]
    dirs_found = []
    files_found = []

    for base in ["/"]:
        if base not in EXCLUDED_DIRS:
            dirs_found += run_find(base, "d")
            files_found += run_find(base, "f")

    if dirs_found:
        results.append("[!] World-writable directories found:")
        for d in dirs_found:
            owner = get_owner(d)
            results.append(f"    {d} (owner: {owner})")
    else:
        results.append("[✓] No world-writable directories found")

    if files_found:
        results.append("[!] World-writable files found:")
        for f in files_found:
            owner = get_owner(f)
            results.append(f"    {f} (owner: {owner})")
    else:
        results.append("[✓] No world-writable files found")

    return "\n".join(results)
