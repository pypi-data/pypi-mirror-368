import subprocess

def check_updates():
    try:
        output = subprocess.check_output(["apt", "list", "--upgradable"], stderr=subprocess.DEVNULL).decode()
        lines = output.strip().splitlines()

        if len(lines) <= 1:
            return "[✓] No packages need updating"

        updates = lines[1:]  # Skip the "Listing..." header
        result = ["[!] System packages with available updates:"]
        result.extend([f"    {line}" for line in updates])
        return "\n".join(result)

    except Exception as e:
        return f"[i] Error checking updates: {e}"
