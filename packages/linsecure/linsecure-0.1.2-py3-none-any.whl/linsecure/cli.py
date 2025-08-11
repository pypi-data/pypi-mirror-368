# linsecure/cli.py
import argparse
from linsecure.core import run_all_checks, run_check_ssh_config, run_check_ssh_ports, run_check_firewall, run_check_updates, run_check_os_info, run_check_file_permissions
import datetime

def main():
    parser = argparse.ArgumentParser(description="Linux vulnerability scanner")
    parser.add_argument("--output", help="Path to save the report", default=None)
    

    parser.add_argument(
        "--ssh-check",
        nargs="+",  # <-- allows multiple values: config ports all
        choices=["config", "ports", "firewall", "updates", "os_info", "file_permissions", "all"],
        help="SSH checks to run: config, ports, or all",
        default=None
    )

    # parser.add_argument("--checks", nargs="+", help="Run multiple checks (e.g., --checks config,ports)")

    args = parser.parse_args()

    # Combine the check types
    # checks = []
    # if args.check:
    #     checks.append(args.check)
    # elif args.checks:
    #     checks.extend(args.checks)
    # else:
        # checks = ["all"]  # Default to "all" if no arguments are given
    report = ""

    if args.ssh_check:
        checks = args.ssh_check

        # Handle 'all' if present
        if "all" in checks:
            checks = ["config", "ports", "firewall", "updates", "os_info", "file_permissions"]

        if "config" in checks:
            report += run_check_ssh_config() + "\n"

        if "ports" in checks:
            report += run_check_ssh_ports() + "\n"

        if "firewall" in checks:
            report += run_check_firewall() + "\n"

        if "updates" in checks:
            report += run_check_updates() + "\n"

        if "os_info" in checks: 
            report += run_check_os_info() + "\n"

        if "file_permissions" in checks:
            report += run_check_file_permissions() + "\n"                
    else:
        report = run_all_checks()
    # # Generate report based on selected check
    # checks = []
    # if args.check == "config":
    #     report = run_check_ssh_config()
    # elif args.check == "ports":
    #     report = run_check_ssh_ports()
    # elif args.check == "firewall":
    #     report = run_check_firewall()
    # elif args.check == "updates":
    #     report = run_check_updates()
    # elif args.check == "os_info":
    #     report = run_check_os_info()
    # elif args.check == "file_permissions":
    #     report = run_check_file_permissions()                
    # elif args.check == "all":
    #     report = run_all_checks()
    # else:
    #     report = run_all_checks()

    if args.output:
        try:
            timestamp = datetime.datetime.now().isoformat()
            with open(args.output, "w") as f:
                f.write(f"# linsecure scan - {timestamp}\n\n")
                f.write(report + "\n")
            print(f"[✓] Report saved to: {args.output}")
        except Exception as e:
            print(f"[!] Failed to save report: {e}")
    else:
        print(report)

if __name__ == "__main__":
    main()
