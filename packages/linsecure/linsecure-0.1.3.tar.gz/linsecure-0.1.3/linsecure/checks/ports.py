import subprocess

def check_open_ports():
    try:
        result = subprocess.check_output(["ss", "-tuln"], stderr=subprocess.DEVNULL).decode()
        lines = result.strip().splitlines()

        if len(lines) <= 1:
            return "[✓] No open ports found"

        ports = lines[1:]  # skip header
        report = ["[!] Open ports detected:"]
        report.extend([f"    {line}" for line in ports])
        return "\n".join(report)

    except FileNotFoundError:
        return "[i] 'ss' command not found on system"

    except Exception as e:
        return f"[i] Error checking open ports: {str(e)}"
