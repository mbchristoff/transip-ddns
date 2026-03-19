#!/usr/bin/env python3
import os
import sys
from datetime import datetime

import requests
from transip import TransIP

# SETTINGS
# The domains to edit (override via DOMAINS env var as a comma-separated list)
domains = [
    '@.domain.tld',
    '*.domain.tld',
    'sub.domain.tld',
    'sub.sub.domain.tld',
]

# Logfile to log output to
logfile = '/var/log/ddns.log'


def log(message):
    """Append a timestamped message to the logfile."""
    time_str = datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')
    with open(logfile, 'a') as f:
        f.write(f"{time_str} {message}\r\n")


# SCRIPT
# Allow domains to be provided via environment variable
domains_env = os.environ.get('DOMAINS', '')
if domains_env:
    domains = [d.strip() for d in domains_env.split(',') if d.strip()]

if not domains:
    sys.exit('No domains in array')

# Get external ip address
try:
    ip_address = requests.get('http://ipecho.net/plain', timeout=10).text.strip()
except requests.RequestException as e:
    sys.exit(f'Failed to retrieve public IP address: {e}')

# Setup TransIP client from environment variables or settings file
try:
    from lib import transip_settings
    login = transip_settings.LOGIN
    private_key = transip_settings.PRIVATE_KEY
    client = TransIP(login=login, private_key=private_key)
except (ImportError, AttributeError):
    login = os.environ.get('TRANSIP_LOGIN', '')
    private_key = os.environ.get('TRANSIP_PRIVATE_KEY', '')
    private_key_file = os.environ.get('TRANSIP_PRIVATE_KEY_FILE', '')
    if not login:
        sys.exit('No TransIP login configured. Set TRANSIP_LOGIN or provide lib/transip_settings.py.')
    if private_key:
        client = TransIP(login=login, private_key=private_key)
    elif private_key_file:
        client = TransIP(login=login, private_key_file=private_key_file)
    else:
        sys.exit('No private key configured. Set TRANSIP_PRIVATE_KEY, TRANSIP_PRIVATE_KEY_FILE, '
                 'or provide lib/transip_settings.py.')

# Loop through domains
for fqdn in domains:
    do_change = False
    record_found = False

    # Separate subdomain and domain from fqdn
    parts = fqdn.split('.')
    subdomain = '.'.join(parts[:-2])
    domainname = '.'.join(parts[-2:])

    # Get the current DNS entries from TransIP
    domain = client.domains.get(domainname)
    dns_entries = domain.dns.list()

    # Loop through records
    for dns_entry in dns_entries:
        # Check records for defined subdomain A record
        if dns_entry.type == 'A' and dns_entry.name == subdomain:
            # Check if the A record has to be updated
            if dns_entry.content != ip_address:
                log(f"Updating old ip {dns_entry.content}, with: {ip_address} for: {subdomain}.{domainname}.")
                print(f"Updating old ip {dns_entry.content}, with: {ip_address} for: {subdomain}.{domainname}")
                dns_entry.content = ip_address
                do_change = True
                record_found = True
            else:
                log(f"No update required, current IP: {dns_entry.content} is unchanged for: {subdomain}.{domainname}.")
                print(f"No update required, current IP: {dns_entry.content} "
                      f"is unchanged for: {subdomain}.{domainname}")
                record_found = True
            break

    if not record_found:
        print(f"Record: {subdomain}.{domainname} not found on TransIP Nameservers.")

    # Update the record when necessary
    if do_change:
        try:
            # Commit the changes to the TransIP DNS servers
            domain.dns.replace(dns_entries)
            # Done
            print('DNS updated successfully!')
        except Exception as e:
            # An error occurred
            print(f'DNS not updated. {str(e)}')
