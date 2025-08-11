# linsecure/core.py
from linsecure.checks.ssh import check_ssh_config
from linsecure.checks.firewall import check_firewall
from linsecure.checks.ports import check_open_ports
from linsecure.checks.updates import check_updates
from linsecure.checks.system import check_os_info
from linsecure.checks.permissions import check_file_permissions

def run_all_checks():
    report = []
    report.append(check_ssh_config())
    report.append(check_firewall())
    report.append(check_open_ports())
    report.append(check_updates())
    report.append(check_os_info())
    report.append(check_file_permissions())
    return "\n\n".join(report)


def run_check_ssh_config():
    report = []
    report.append(check_ssh_config())
    return "\n\n".join(report)

def run_check_ssh_ports():
    report = []
    report.append(check_open_ports())
    return "\n\n".join(report)


def run_check_firewall():
    report = []
    report.append(check_firewall())
    return "\n\n".join(report)


def run_check_updates():
    report = []
    report.append(check_updates())
    return "\n\n".join(report)


def run_check_os_info():
    report = []
    report.append(check_os_info())
    return "\n\n".join(report)


def run_check_file_permissions():
    report = []
    report.append(check_file_permissions())
    return "\n\n".join(report)
