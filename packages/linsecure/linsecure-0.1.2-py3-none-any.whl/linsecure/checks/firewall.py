import subprocess

def check_firewall():
    try:
        output = subprocess.check_output(["ufw", "status"], stderr=subprocess.STDOUT).decode().lower()

        if "inactive" in output:
            return "[i] Firewall Check:\n[!] UFW firewall is INACTIVE"
        elif "active" in output:
            return "[i] Firewall Check:\n[✓] UFW firewall is active"
        else:
            return "[i] Firewall Check:\n[i] UFW status is unclear"

    except FileNotFoundError:
        return "[i] Firewall Check:\n[i] UFW is not installed on the system"

    except subprocess.CalledProcessError as e:
        return f"[i] Firewall Check:\n[i] Error checking UFW status:\n{e.output.decode().strip()}"
