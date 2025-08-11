import os

def check_ssh_config():
    results = []
    ssh_config_path = "/etc/ssh/sshd_config"

    if not os.path.exists(ssh_config_path):
        return "[i] SSH config not found (maybe OpenSSH not installed?)"

    with open(ssh_config_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip().lower()

        if line.startswith("permitrootlogin"):
            if "yes" in line:
                results.append("[!] SSH allows root login – DISCOURAGED")
            else:
                results.append("[✓] SSH root login is disabled")

        if line.startswith("passwordauthentication"):
            if "yes" in line:
                results.append("[!] SSH uses password authentication – Consider disabling")
            else:
                results.append("[✓] SSH password login is disabled (good)")

    if results:
        return "[i] SSH Configuration Check:\n" + "\n".join(results)
    else:
        return "[i] No relevant SSH settings found in sshd_config"
